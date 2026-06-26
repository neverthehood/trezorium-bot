# src/main_dating.py
# Trezorium Dating Bot

import asyncio
from aiohttp import web
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

from src.config import cfg
from src.question_loader import load_bank
from src.models import SessionState
from src.mods import compute_mods
from src.indotype_resolver import resolve_indotype
from src.gpt_messages import generate_first_message
from src.supabase_client import save_user, save_result, get_all_results, delete_old_result, get_user

router = Router()

bank = load_bank("pack_dating_v1.json")

_sessions = {}

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ONBOARDING_COUNT = 12

TYPE_NAMES = {
    "G1AA": "Профессор", "G1AB": "Лаборант", "G1BA": "Философ", "G1BB": "Писатель",
    "G2AA": "Инженер", "G2AB": "Механик", "G2BA": "Блогер", "G2BB": "Полиглот",
    "S1AA": "Романтик", "S1AB": "Альтруист", "S1BA": "Лидер", "S1BB": "Душа компании",
    "S2AA": "Перфекционист", "S2AB": "Рекордсмен", "S2BA": "Воин", "S2BB": "Роковая личность",
    "T1AA": "Экстремал", "T1AB": "Марафонец", "T1BA": "Артист", "T1BB": "Спасатель",
    "T2AA": "Садовник", "T2AB": "Строитель", "T2BA": "Музыкант", "T2BB": "Ювелир",
    "K1AA": "Изобретатель", "K1AB": "Проводник", "K1BA": "Мастер-самоделкин", "K1BB": "Бионик",
    "K2AA": "Художник", "K2AB": "Скульптор", "K2BA": "Режиссёр", "K2BB": "Бунтарь",
}

TYPE_DESCRIPTIONS = {
    "G1AA": "Ты — стратег. Видишь общую картину там, где остальные видят буквы. В отношениях ищешь партнёра, с которым можно обсудить теорию струн за утренним кофе.",
    "G1AB": "Ты — Лаборант. Любишь детали, точность и порядок. В отношениях ценишь надёжность и предсказуемость.",
    "G1BA": "Ты — Философ. Вечно ищешь смысл во всём. Ищешь того, кто поймёт твои сложные мысли без лишних слов.",
    "G1BB": "Ты — Писатель. Слова — твоя стихия. В отношениях — романтик-интеллектуал.",
    "G2AA": "Ты — Инженер. Любишь, когда всё работает. Практичный, надёжный, с лёгким налётом ворчливости.",
    "G2AB": "Ты — Механик. Любишь разбираться, как устроен мир. Ищешь того, кто оценит твою способность починить всё, кроме своей личной жизни.",
    "G2BA": "Ты — Блогер. Умеешь рассказывать истории. В отношениях ищешь со-автора.",
    "G2BB": "Ты — Полиглот. Понимаешь всех и говоришь на языке каждого. В паре ты — дипломат и миротворец.",
    "S1AA": "Ты — Романтик. Веришь в любовь до гроба. Ищешь того, кто не разобьёт твоё хрупкое сердце.",
    "S1AB": "Ты — Альтруист. Помогать другим — твоё призвание. Ищи того, кто умеет принимать заботу и отвечать тем же.",
    "S1BA": "Ты — Лидер. У тебя есть харизма и видение. В отношениях нужен партнёр, который не боится твоей силы.",
    "S1BB": "Ты — Душа компании. Твоя суперсила — располагать к себе людей.",
    "S2AA": "Ты — Перфекционист. Всё должно быть идеально. Ищешь партнёра, который выдержит твои стандарты.",
    "S2AB": "Ты — Рекордсмен. Ставишь цели и достигаешь их. В отношениях ищешь того, кто будет болеть за тебя.",
    "S2BA": "Ты — Воин. Защищаешь тех, кто тебе дорог. В паре ты — надёжный тыл.",
    "S2BB": "Ты — Роковая личность. Твоя энергия притягивает и пугает одновременно.",
    "T1AA": "Ты — Экстремал. Тебе нужен адреналин. В паре нужен человек, который не будет просить тебя успокоиться.",
    "T1AB": "Ты — Марафонец. Выносливый, упёртый, идёшь до конца. В отношениях стабилен и надёжен.",
    "T1BA": "Ты — Артист. Любишь быть в центре внимания. Ищешь зрителя, который будет аплодировать стоя.",
    "T1BB": "Ты — Спасатель. Бросаешься помогать всем подряд. Ищи того, кто спасёт тебя от самого себя.",
    "T2AA": "Ты — Садовник. Любишь выращивать — растения, идеи, отношения. Ищешь партнёра, с которым хочется расти вместе.",
    "T2AB": "Ты — Строитель. Созидатель по натуре. Ищешь партнёра, с которым можно построить общее будущее.",
    "T2BA": "Ты — Музыкант. Тонко воспринимаешь красоту. В отношениях ищешь гармонии.",
    "T2BB": "Ты — Ювелир. Точность, терпение, внимание к каждой детали. В отношениях разборчив.",
    "K1AA": "Ты — Изобретатель. Генерируешь идеи пачками. В отношениях ищешь того, кто не скажет это невозможно.",
    "K1AB": "Ты — Проводник. Видишь то, что скрыто от других. Ищешь попутчика для этого путешествия.",
    "K1BA": "Ты — Мастер-самоделкин. Твои руки и голова работают в связке.",
    "K1BB": "Ты — Бионик. Вдохновляешься природой и технологиями. В отношениях ищешь естественности и глубины.",
    "K2AA": "Ты — Художник. Видишь мир в цвете и форме. Ищешь музу, а не просто партнёра.",
    "K2AB": "Ты — Скульптор. Из любого материала делаешь шедевр. Ищешь того, кто позволит себя лепить.",
    "K2BA": "Ты — Режиссёр. Организуешь хаос. В отношениях ставишь спектакль для двоих.",
    "K2BB": "Ты — Бунтарь. Не потому что модно, а потому что иначе не умеешь.",
}


def find_q(qid: str):
    for q in bank.questions:
        if q.id == qid:
            return q
    return None


def enum_opts(q):
    return [(LETTERS[i], o) for i, o in enumerate(q.options)]


def kb_single(q):
    rows, row = [], []
    for i, (letter, o) in enumerate(enum_opts(q), 1):
        row.append(InlineKeyboardButton(text=letter, callback_data=f"ans:{q.id}:{o.id}"))
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def safe_answer(cb, text=None):
    try:
        if text:
            await cb.answer(text)
        else:
            await cb.answer()
    except Exception:
        pass


async def send_question(m, st, qid):
    q = find_q(qid)
    if not q:
        await m.answer("Что-то пошло не так...")
        return

    st.asked.append(qid)
    st.answers.setdefault(qid, {})

    lines = []
    lines.append(f"*{q.text}*")
    lines.append("")
    for letter, o in enum_opts(q):
        lines.append(f"{letter}) {o.label}")

    await m.answer("\n".join(lines), reply_markup=kb_single(q), parse_mode="Markdown")


async def finish_test(m, st):
    mods_result = compute_mods(st.answers, bank, st.vectors)
    raw_mods = mods_result.get("raw", {})

    indotype = resolve_indotype(mods_result)
    code = indotype.get("code", "—")
    human_name = TYPE_NAMES.get(code, code)
    description = TYPE_DESCRIPTIONS.get(code, "Уникальный типаж!")

    # Удаляем старый результат (повторное прохождение)
    try:
        await delete_old_result(m.chat.id)
    except Exception:
        pass

    # Сохраняем
        print(f"[DB] Save user {m.chat.id}...")
    try:
        raw_gender = getattr(st, 'gender', '')
        gender = "M" if raw_gender == "male" else "F" if raw_gender == "female" else ""
        age = getattr(st, 'age', 0)
        looking_for = getattr(st, 'looking_for', '') or ''
        u = await save_user(m.chat.id, m.from_user.username, gender=gender, age=age, looking_for=looking_for)
        print(f"[DB] User saved: {u}")
        raw_gender2 = getattr(st, 'gender', '')
        gender2 = "M" if raw_gender2 == "male" else "F" if raw_gender2 == "female" else ""
        r = await save_result(m.chat.id, code, st.vectors, raw_mods, gender=gender2, age=age, looking_for=looking_for)
        print(f"[DB] Result saved: {r}")
    except Exception as e:
        import traceback
        print(f"[DB] Error: {e}")
        traceback.print_exc()

    # Результат
    result_lines = []
    result_lines.append(f"\U0001f9e9 *Твой типаж:* {human_name}")
    result_lines.append("")
    result_lines.append(f"_{description}_")
    result_lines.append("")

    match = await find_match(m.chat.id, code, raw_mods)

    if match:
        match_user_id, match_code, match_mods, score = match
        match_name = TYPE_NAMES.get(match_code, match_code)
        result_lines.append("\U0001f3af *Мы нашли твою половинку!*")
        result_lines.append("")
        result_lines.append(f"Совместимость: *{score:.0f}%*")
        result_lines.append(f"Типаж: {match_name}")
        result_lines.append("")
        result_lines.append(f"Напиши @{match_user_id} — вы созданы друг для друга!")
    else:
        result_lines.append("\U0001f50d *Ищем твоё сокровище...*")
        result_lines.append("")
        result_lines.append("Пока ты единственный в своём типаже.")
        result_lines.append("Но скоро я найду того, кто тебе подходит!")
        result_lines.append("")
        result_lines.append("\U0001f447 А пока — поделись результатом с друзьями!")

        # Предварительный результат + ежедневные вопросы
        result_lines.append("")
        result_lines.append("—")
        result_lines.append("")
        result_lines.append("\U0001f4c8 *Это предварительный результат!*")
        result_lines.append("")
        result_lines.append("Чтобы получить полный портрет и точный мэтч,")
        result_lines.append("я буду задавать тебе по 4 вопроса каждый день.")
        result_lines.append("")
        result_lines.append(f"Прогресс: {len(st.answers)}/48")
        result_lines.append("")
        result_lines.append("Завтра будет новый блок — возвращайся! \U0001f525")

        st.daily_mode = True

    result_text = "\n".join(result_lines)

    await m.answer(result_text, parse_mode="Markdown")


async def find_match(user_id, code, mods):
    try:
        all_results = await get_all_results()
    except Exception:
        return None

    from src.matcher import compute_match, get_explanation
    from datetime import datetime, timedelta

    st = _sessions.get(user_id)
    user_gender = getattr(st, 'gender', '') if st else ''
    user_looking = getattr(st, 'looking_for', '') if st else ''

    if not user_gender or not user_looking:
        # Пробуем из БД
        try:
            user_data = await get_user(user_id)
            if user_data:
                user_gender = user_data.get('gender', '')
                user_looking = user_data.get('looking_for', '')
        except Exception:
            pass

    best_score = 0
    best_match = None
    now = datetime.utcnow()

    for result in all_results:
        if result["telegram_id"] == user_id:
            continue

        tid = result["telegram_id"]

        # Проверка на блокировку 7 дней
        try:
            from src.supabase_client import get_client
            client = get_client()
            block = client.table("match_blocks") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("blocked_user_id", tid) \
                .execute()
            if block.data:
                blocked_at = block.data[0].get("created_at")
                if blocked_at:
                    # Парсим ISO дату
                    btime = blocked_at
                    if isinstance(btime, str):
                        btime = btime.replace('Z', '+00:00')
                        from dateutil import parser
                        btime = parser.parse(btime)
                    if (now - btime).days < 7:
                        continue
        except Exception:
            pass

        # Фильтр по полу
        their_gender = result.get("gender", "")
        their_looking = result.get("looking_for", "")

        # match: gender M -> looking_for F (ищем девушек)
        # user_looking A — подходят все
        if user_looking != "A":
            if their_gender != user_looking:
                continue
        if their_looking != "A" and their_looking not in ("A", user_gender):
            continue

        # Фильтр по возрасту (плюс-минус 5 лет)
        user_age = getattr(st, 'age', 0) if st else 0
        their_age = result.get("age", 0)
        if user_age and their_age:
            if abs(user_age - their_age) > 5:
                continue

        their_mods = result.get("mods", {})
        if not their_mods:
            continue
        score = compute_match(mods, their_mods)
        if score > best_score:
            best_score = score
            best_match = (tid, result["indotype_code"], their_mods, score)

    if best_score >= 50:
        return best_match
    return None


# ------------------------------------------------------------
# Handlers
# ------------------------------------------------------------

@router.message(CommandStart())
async def h_start(m: Message):
    welcome = (
        "👋 *Trezorium* — сокровищница твоей половинки.\n\n"
        "Я считаю, что каждый человек — уникальное сокровище "
        "со своим типом мышления, чувств и энергии.\n"
        "Большинство знакомств — лотерея. Я хочу, чтобы это была точная наука.\n\n"
        "Я задам 12 вопросов, чтобы узнать твой типаж, и найду того, кто тебе подходит.\n\n"
        "Первые 200 пользователей — *бесплатный доступ навсегда* 🎁"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🚀 Начнём!", callback_data="start_onboarding")]]
    )
    await m.answer(welcome, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("help"))
async def h_help(m: Message):
    help_text = (
        "\U0001f916 *Trezorium — команды*\n\n"
        "/start — начать тест\n"
        "/daily — ежедневные вопросы\n"
        "/profile — мой профиль\n"
        "/agreement — пользовательское соглашение\n"
        "/privacy — политика конфиденциальности\n"
        "/delete_me — удалить данные\n"
        "/help — эта подсказка"
    )
    await m.answer(help_text, parse_mode="Markdown")


@router.message(Command("daily"))
async def h_daily(m: Message):
    await m.answer("Ежедневные вопросы будут добавлены в следующем обновлении.")


@router.message(Command("profile"))
async def h_profile(m: Message):
    try:
        result = await get_latest_result(m.chat.id)
    except Exception:
        result = None
    if not result:
        await m.answer("Ты ещё не проходил тест. Напиши /start")
        return

    code = result.get("indotype_code", "—")
    human_name = TYPE_NAMES.get(code, code)
    description = TYPE_DESCRIPTIONS.get(code, "")

    mods = result.get("mods", {})
    top_mods = sorted(mods.items(), key=lambda x: -abs(x[1]))[:5]
    mods_str = "\n".join(f"- {k}: {v:.1f}" for k, v in top_mods)

    profile = (
        f"\U0001f464 *Твой профиль*\n\n"
        f"\U0001f9e9 *{human_name}* (`{code}`)\n"
        f"_{description}_\n\n"
        f"\U0001f4ca *Основные черты:*\n{mods_str}\n\n"
        f"\U0001f50d Ищем твоё сокровище..."
    )
    await m.answer(profile, parse_mode="Markdown")


@router.message(Command("delete_me"))
async def h_delete(m: Message):
    await m.answer(
        "\u26a0\ufe0f *Удаление данных*\n\n"
        "Все твои ответы и профиль будут безвозвратно удалены.\n\n"
        "Если уверен — напиши */confirm_delete*",
        parse_mode="Markdown"
    )


@router.message(Command("confirm_delete"))
async def h_confirm_delete(m: Message):
    try:
        from src.supabase_client import get_client
        client = get_client()
        client.table("results").delete().eq("telegram_id", m.chat.id).execute()
        client.table("users").delete().eq("telegram_id", m.chat.id).execute()
    except Exception as e:
        print(f"[DB] Delete error: {e}")
    _sessions.pop(m.chat.id, None)
    await m.answer(
        "\u2705 *Все данные удалены.*\n\n"
        "Если захочешь вернуться — напиши /start",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "start_onboarding")
async def h_start_onboarding(cb: CallbackQuery):
    await safe_answer(cb)
    st = SessionState(chat_id=cb.message.chat.id)
    _sessions[cb.message.chat.id] = st
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👦 Парень", callback_data="gender_M")],
            [InlineKeyboardButton(text="👧 Девушка", callback_data="gender_F")],
        ]
    )
    await cb.message.answer("*Ты парень или девушка?*", reply_markup=keyboard, parse_mode="Markdown")
    st.waiting_for = "gender"


@router.callback_query(F.data.startswith("gender_"))
async def h_onboarding_gender(cb: CallbackQuery):
    await safe_answer(cb)
    st = _sessions.get(cb.message.chat.id)
    if not st:
        return
    
        st.gender = "male" if cb.data.endswith("_M") else "female"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👦 Парня", callback_data="looking_M")],
            [InlineKeyboardButton(text="👧 Девушку", callback_data="looking_F")],
            [InlineKeyboardButton(text="🤝 Обоих", callback_data="looking_A")],
        ]
    )
    await cb.message.answer("🔍 *Кого ты ищешь?*", reply_markup=keyboard, parse_mode="Markdown")
    st.waiting_for = "looking_for"


@router.callback_query(F.data.startswith("looking_"))
async def h_onboarding_looking(cb: CallbackQuery):
    await safe_answer(cb)
    st = _sessions.get(cb.message.chat.id)
    if not st:
        return
    
    st.looking_for = cb.data.split("_")[1]
    
    await cb.message.answer(
        "🧑‍🎓 *Сколько тебе лет?*\n\n"
        "Напиши число (например: 25)",
        parse_mode="Markdown"
    )
    st.waiting_for = "age"


@router.message(F.text & ~F.command)
async def h_onboarding_age(m: Message):
    """Принимаем возраст текстом."""
    st = _sessions.get(m.chat.id)
    if not st or getattr(st, 'waiting_for', None) != "age":
        return
    
    text = m.text.strip()
    try:
        age = int(text)
        if age < 18:
            await m.answer("⚠️ Trezorium — приложение 18+.")
            return
        if age > 120:
            await m.answer("😊 Ну не может быть столько, напиши честно:")
            return
        st.age = age
        st.waiting_for = None
        # Начинаем тест
        q = bank.questions[0]
        await send_question(m, st, q.id)
    except ValueError:
        await m.answer("Напиши число — сколько тебе лет 😊")


@router.callback_query(F.data.startswith("ans:"))
async def ans(cb: CallbackQuery):
    _, qid, opt_id = cb.data.split(":", 2)
    st = _sessions.get(cb.message.chat.id)
    if not st:
        await safe_answer(cb, "Начните с /start")
        return
    if st.answers.get(qid, {}).get("single"):
        await safe_answer(cb, "Уже отвечено")
        return
    q = find_q(qid)
    if not q:
        await safe_answer(cb)
        return
    st.answers[qid]["single"] = opt_id
    st.answers[qid]["answer"] = opt_id
    opt = next((o for o in q.options if o.id == opt_id), None)
    if opt:
        from src.engine import apply_weights
        apply_weights(st, opt.weights or {}, 1.0)
    await safe_answer(cb)

    asked_count = len(st.asked)
    if asked_count < len(bank.questions):
        next_q = bank.questions[asked_count]
        await send_question(cb.message, st, next_q.id)
    else:
        await finish_test(cb.message, st)


async def set_commands(bot):
    commands = [
        BotCommand(command="start", description="Начать тест"),
        BotCommand(command="daily", description="Ежедневные вопросы"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="agreement", description="Пользовательское соглашение"),
        BotCommand(command="privacy", description="Политика конфиденциальности"),
        BotCommand(command="delete_me", description="Удалить данные"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)


async def health_check(request):
    return web.Response(text="OK")


async def start_health_server():
    import os
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[Health] Server started on port {port}")


async def main():
    # Настройка логирования в файл и консоль
    log_format = "%(asctime)s | %(levelname)s | %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log", encoding="utf-8"),
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Бот запускается...")
    
    # Запускаем health check сервер в фоне
    asyncio.create_task(start_health_server())
    
    logger.info("Проверяю BOT_TOKEN...")
    if not cfg.BOT_TOKEN:
        logger.error("BOT_TOKEN не задан!")
        return
    logger.info("BOT_TOKEN присутствует")
    
    bot = Bot(cfg.BOT_TOKEN)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхук удалён")
    except Exception as e:
        logger.warning(f"Ошибка удаления вебхука: {e}")
    await set_commands(bot)
    logger.info("Команды установлены")
    
    dp = Dispatcher()
    dp.include_router(router)
    logger.info("Роутер подключён, стартую polling...")
    print("Trezorium Dating запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
