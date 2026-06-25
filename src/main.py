from pathlib import Path
from typing import Optional
from src.loader import load_catalog
import asyncio
import logging
import datetime
import random
import time
import hashlib

from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

from .config import cfg
from .question_loader import load_bank
from .models import SessionState, Question, Option
from .engine import apply_weights
from .mods import compute_mods
from src.result_renderer import render_report, render_html_report, render_short_card


ROOT = Path(__file__).resolve().parent.parent

router = Router()
bank = load_bank()
_sessions = {}
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

async def safe_answer(cb: CallbackQuery, text: Optional[str] = None):
    try:
        if text:
            await cb.answer(text)
        else:
            await cb.answer()
    except TelegramBadRequest:
        pass


def find_q(qid: str) -> Optional[Question]:
    for q in bank.questions:
        if q.id == qid:
            return q
    return None


def st_for(chat_id: int) -> SessionState:
    st = _sessions.get(chat_id)
    if not st:
        st = SessionState(chat_id=chat_id)
        # Сразу создаём маршрут, чтобы не было пустых отчётов
        st.route_core = build_route(48, chat_id, "adult", "classic")
        _sessions[chat_id] = st
    return st


def enum_opts(q: Question):
    return [(LETTERS[i], o) for i, o in enumerate(q.options)]


def kb_single(q: Question) -> InlineKeyboardMarkup:
    rows, row = [], []
    for i, (letter, o) in enumerate(enum_opts(q), 1):
        row.append(
            InlineKeyboardButton(
                text=letter,
                callback_data=f"ans:{q.id}:{o.id}",
            )
        )
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _rand(seed_str: str):
    rnd = random.Random()
    h = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16)
    rnd.seed(h)
    return rnd


def build_route(sample_size: int, chat_id: int, mode: str, style: str) -> list:
    singles = [
        q for q in bank.questions
        if q.format == "single"
    ]
    ids = [q.id for q in singles]
    rnd = _rand(f"{chat_id}-{datetime.date.today().isoformat()}")
    rnd.shuffle(ids)
    return ids[:min(sample_size, len(ids))]


def next_in_route(st: SessionState) -> Optional[str]:
    asked = set(st.asked or [])
    for qid in st.route_core or []:
        if qid not in asked:
            return qid
    return None


# ------------------------------------------------------------
# Question sending
# ------------------------------------------------------------

async def send_q(m: Message, st: SessionState, qid: str):
    q = find_q(qid)
    if not q:
        await m.answer("Вопрос не найден")
        return

    st.asked.append(qid)
    st.answers.setdefault(qid, {})
    st.answers[qid]["_asked_ts"] = time.time()

    lines = []

    if q.intro:
        lines.append(q.intro)
        lines.append("")

    lines.append(f"*{q.text}*")
    lines.append("")
    for letter, o in enum_opts(q):
        lines.append(f"{letter}) {o.label}")

    await m.answer(
        "\n".join(lines),
        reply_markup=kb_single(q),
        parse_mode="Markdown"
    )


# ------------------------------------------------------------
# Finish and report
# ------------------------------------------------------------

async def finish_and_report(m: Message, st: SessionState):
    try:
        # Отладочный вывод
        print(f"\n=== FINISH_AND_REPORT ===")
        print(f"Answers count: {len(st.answers)}")
        print(f"Vectors keys: {list(st.vectors.keys())}")
        print(f"Route length: {len(st.route_core)}")

        report_data = render_report(
            answers=st.answers,
            vectors=st.vectors,
            catalog=bank
        )

        print(f"Indotype: {report_data.get('indotype', {}).get('code', '?')}")
        print(f"Pure vectors: {report_data.get('vectors', {})}")
        print(f"Raw mods: {report_data.get('raw_mods', {})}")
        print("===========================\n")

    except Exception as e:
        import traceback
        traceback.print_exc()
        await m.answer(f"⚠️ Ошибка при формировании отчёта:\n<code>{e}</code>", parse_mode="HTML")
        return

    indotype = report_data.get("indotype", {})
    mods_raw = report_data.get("raw_mods", {})

    html = render_html_report(
        code=indotype,
        vectors=report_data.get("vectors", {}),
        answers=report_data.get("answers", {}),
        catalog=load_catalog(),
        mods_result={"raw": mods_raw}
    )

    try:
        reports_dir = ROOT / "data/reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        fname = f"report_{m.chat.id}_{int(time.time())}.html"
        fpath = reports_dir / fname
        fpath.write_text(html, encoding="utf-8")

        # Короткая карточка результата в чат
        short_card = render_short_card(
            code=indotype.get("code", "—"),
            vectors=report_data.get("vectors", {})
        )
        await m.answer(short_card, parse_mode="Markdown")

        # Полный HTML-отчёт
        await m.answer_document(
            FSInputFile(fpath, filename=fname),
            caption="📄 Полный отчёт Trezorium"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        await m.answer("⚠️ Отчёт сформирован, но файл отправить не удалось.")


async def after(m: Message, st: SessionState):
    # Диагностика
    asked_count = len(st.asked) if st.asked else 0
    route_len = len(st.route_core) if st.route_core else 0
    print(f"[after] chat={m.chat.id} asked={asked_count}/{route_len}")
    
    # Если маршрут пуст — создаём новый
    if not st.route_core:
        print(f"[after] WARNING: route_core is empty! Creating new route.")
        st.route_core = build_route(48, m.chat.id, "adult", "classic")
    
    # Если ответили на все вопросы — финиш
    if len(st.asked) >= len(st.route_core):
        print(f"[after] All {len(st.route_core)} questions answered -> finish!")
        await finish_and_report(m, st)
        return
    
    qid = next_in_route(st)
    if qid is None:
        print(f"[after] next_in_route returned None but not all answered -> fallback")
        # Берём первый неотвеченный напрямую
        for qid_candidate in st.route_core:
            if qid_candidate not in (st.asked or []):
                qid = qid_candidate
                break
        if qid is None:
            await finish_and_report(m, st)
            return
    
    await send_q(m, st, qid)


# ------------------------------------------------------------
# Handlers
# ------------------------------------------------------------

@router.message(CommandStart())
async def h_start(m: Message):

    welcome = (
        "🧠 *Добро пожаловать в Trezorium*\n\n"
        "Этот тест анализирует:\n"
        "• стиль мышления\n"
        "• эмоциональные реакции\n"
        "• поведенческие паттерны\n"
        "• когнитивные модификаторы\n\n"
        "⏳ Время прохождения: ~7 минут.\n"
        "Отвечайте интуитивно."
    )

    await m.answer(welcome, parse_mode="Markdown")

    st = SessionState(
        chat_id=m.chat.id,
        started_at=datetime.datetime.utcnow().isoformat() + "Z"
    )

    _sessions[m.chat.id] = st

    st.route_core = build_route(
        48,
        m.chat.id,
        "adult",
        "classic"
    )

    await send_q(m, st, st.route_core[0])


@router.message(Command("reset"))
async def h_reset(m: Message):
    st = SessionState(
        chat_id=m.chat.id,
        started_at=datetime.datetime.utcnow().isoformat() + "Z"
    )
    _sessions[m.chat.id] = st
    st.route_core = build_route(48, m.chat.id, "adult", "classic")
    await send_q(m, st, st.route_core[0])


@router.callback_query(F.data.startswith("ans:"))
async def ans(cb: CallbackQuery):
    _, qid, opt_id = cb.data.split(":", 2)
    st = st_for(cb.message.chat.id)
    
    print(f"[ans] chat={cb.message.chat.id} qid={qid} opt={opt_id}")

    q = find_q(qid)
    if not q:
        await safe_answer(cb)
        return

    st.answers.setdefault(qid, {})
    
    # Защита: если на этот вопрос уже отвечали — игнорируем
    if st.answers[qid].get("single") is not None:
        print(f"[ans] chat={cb.message.chat.id} qid={qid} ALREADY ANSWERED, skip")
        await safe_answer(cb, "Вы уже ответили на этот вопрос")
        return
    
    st.answers[qid]["single"] = opt_id
    st.answers[qid]["answer"] = opt_id

    opt = next((o for o in q.options if o.id == opt_id), None)
    if opt:
        apply_weights(st, opt.weights or {}, 1.0)

    await safe_answer(cb)
    await after(cb.message, st)


# ------------------------------------------------------------
# Runner
# ------------------------------------------------------------

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(cfg.BOT_TOKEN)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is starting... (polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
