# fix_ru_texts_blocks.py — перезаписывает русские тексты без «кракозябр»
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = (s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    "))

def put_block(s, header_regex, new_block):
    pat = re.compile(header_regex, re.M|re.S)
    m = pat.search(s)
    if not m:
        return s + "\n\n" + new_block.strip() + "\n"
    return s[:m.start()] + new_block.strip() + "\n" + s[m.end():]

# 1) length_hint()
length_block = r"""
def length_hint() -> str:
    return (
        "Выбери объём теста:\n\n"
        "• Экспресс — около 24 вопросов (≈10–12 минут)\n"
        "• Стандарт — около 48 вопросов (≈20–25 минут)\n"
        "• Глубокий — около 72 вопросов (≈35–45 минут)"
    )
"""
s = put_block(s, r'(?ms)^\s*def\s+length_hint\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:def|async\s+def|@|class)\b|\Z)', length_block)

# 2) kb_format / ask_format / set_format (сообщения и кнопки)
format_block = r"""
def kb_format():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="Классика", callback_data="fmt:classic")],
        [B(text="Истории",  callback_data="fmt:story")],
    ])

async def ask_format(m, st):
    txt = (
        "Выбери формат вопросов:\n\n"
        "• Классика — короткие, чёткие ситуации.\n"
        "• Истории — развернутые мини-сюжеты с погружением."
    )
    await m.answer(txt, reply_markup=kb_format())

@router.callback_query(F.data.startswith("fmt:"))
async def set_format(cb: CallbackQuery):
    _, val = cb.data.split(":", 1)
    st = st_for(cb.message.chat.id)
    st.style = val if val in ("classic","story") else "classic"
    await safe_answer(cb, "Ок")
    await cb.message.answer(length_hint(), reply_markup=kb_length())
"""
s = put_block(s, r'(?ms)^\s*def\s+kb_format\s*\([^)]*\)\s*:\s*.*?@router\.callback_query\(F\.data\.startswith\("fmt:"\)\)\s*.*?def\s+set_format\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:def|async\s+def|@|class)\b|\Z)', format_block)

# 3) set_aud — «Укажи пол.»
aud_block = r"""
@router.callback_query(F.data.startswith("aud:"))
async def set_aud(cb: CallbackQuery):
    _, val = cb.data.split(":", 1)
    st = st_for(cb.message.chat.id)
    st.mode = val if val in ("child","teen","adult") else "teen"
    await safe_answer(cb, "Ок")
    await cb.message.answer("Укажи пол.", reply_markup=kb_gender())
"""
s = put_block(s, r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("aud:"\)\)\s*.*?def\s+set_aud\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:def|async\s+def|@|class)\b|\Z)', aud_block)

# 4) set_gender — «Сохранено» и вызов ask_format
gender_pat = re.compile(r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("gender:"\)\)\s*.*?def\s+set_gender\s*\([^)]*\)\s*:\s*(.*?)\n(?=^\s*(?:def|async\s+def|@|class)\b|\Z)')
m = gender_pat.search(s)
if m:
    body = m.group(1)
    body = re.sub(r'await\s+safe_answer\(cb,\s*".*?"\s*\)', 'await safe_answer(cb, "Сохранено")', body)
    body = re.sub(r'await\s+cb\.message\.answer\(\s*length_hint\(\)\s*,\s*reply_markup\s*=\s*kb_length\(\)\s*\)',
                  'await ask_format(cb.message, st)', body)
    s = s[:m.start(1)] + body + s[m.end(1):]

# 5) set_length — «Объём выбран», «Начинаем!», старт первого вопроса
setlen_block = r"""
@router.callback_query(F.data.startswith("len:"))
async def set_length(cb: CallbackQuery):
    _, val = cb.data.split(":", 1)
    st = st_for(cb.message.chat.id)
    st.length = val if val in ("express","standard","deep") else "standard"
    await safe_answer(cb, "Объём выбран")
    print(f"[DEBUG] set_length: length={st.length} mode={getattr(st,'mode',None)} style={getattr(st,'style',None)}")
    intro = _plan_and_start(cb, st)
    if not getattr(st, "route_core", None):
        await cb.message.answer("Пока не нашлось вопросов для выбранных настроек. Попробуй другой формат/объём.")
        return
    print(f"[DEBUG] route size: {len(st.route_core)}")
    await cb.message.answer("Начинаем!")
    await cb.message.answer(intro)
    await send_q(cb.message, st, st.route_core[0])
"""
s = put_block(s, r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("len:"\)\)\s*.*?def\s+set_length\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:def|async\s+def|@|class)\b|\Z)', setlen_block)

# 6) Чистим явные «кракозябры» во всём файле, если остались
pairs = {
    "РќР°С‡Р°Р»Рё Р·Р°РЅРѕРІРѕ.": "Начали заново.",
    "РЈРєР°Р¶Рё РїРѕР».": "Укажи пол.",
    "РЎРѕС…СЂР°РЅРµРЅРѕ": "Сохранено",
    "РћРє": "Ок",
    "РћР±СЉС‘Рј РІС‹Р±СЂР°РЅ": "Объём выбран",
    "Р’С‹Р±СЂР°РЅРѕ:": "Выбрано:",
    "РўРµРїРµСЂСЊ": "Теперь",
}
for bad, good in pairs.items():
    s = s.replace(bad, good)

# сохранить
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: русские тексты и кнопки обновлены; «кракозябры» убраны.")
