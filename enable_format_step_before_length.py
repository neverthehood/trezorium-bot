# enable_format_step_before_length.py — вставляет шаг выбора формата перед выбором объёма
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = (s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    "))

# 1) Блок выбора формата (kb_format, ask_format, set_format) — добавим/обновим
block = (
    "def kb_format():\n"
    "    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B\n"
    "    return InlineKeyboardMarkup(inline_keyboard=[\n"
    "        [B(text=\"Классика\", callback_data=\"fmt:classic\")],\n"
    "        [B(text=\"Истории\",  callback_data=\"fmt:story\")],\n"
    "    ])\n"
    "\n"
    "async def ask_format(m, st):\n"
    "    txt = (\n"
    "        \"Выбери формат вопросов:\\n\\n\"\n"
    "        \"• Классика — короткие, чёткие ситуации.\\n\"\n"
    "        \"• Истории — развернутые мини-сюжеты с погружением.\"\n"
    "    )\n"
    "    await m.answer(txt, reply_markup=kb_format())\n"
    "\n"
    "@router.callback_query(F.data.startswith(\"fmt:\"))\n"
    "async def set_format(cb: CallbackQuery):\n"
    "    _, val = cb.data.split(\":\", 1)\n"
    "    st = st_for(cb.message.chat.id)\n"
    "    st.style = val if val in (\"classic\",\"story\") else \"classic\"\n"
    "    await safe_answer(cb, \"Ок\")\n"
    "    await cb.message.answer(length_hint(), reply_markup=kb_length())\n"
    "\n"
)

# вставим блок перед set_aud (если найдём), иначе — в начало «хэндлерной» зоны
m_aud = re.search(r'(?m)^@(?:dp|router)\.callback_query\(F\.data\.startswith\(\"aud:\"\)\)\s*', s)
if m_aud:
    s = s[:m_aud.start()] + block + s[m_aud.start():]
else:
    # вставим после импортов aiogram
    s = re.sub(r'(?m)^(from aiogram .*?\n)', r'\1' + block, s, count=1)

# 2) set_gender: вместо вопроса про объём — спросим формат
pat_gender = re.compile(
    r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\(\"gender:\"\)\)\s*?\n\s*async\s+def\s+set_gender\s*\([^)]*\)\s*:\s*(.*?)\n(?=^\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z)',
    re.M
)
m = pat_gender.search(s)
if m:
    body = m.group(1)
    # заменим строку, где сейчас спрашивается объём
    body_new = re.sub(
        r'await\s+cb\.message\.answer\s*\(\s*length_hint\(\)\s*,\s*reply_markup\s*=\s*kb_length\(\)\s*\)\s*',
        'await ask_format(cb.message, st)',
        body,
        count=1
    )
    s = s[:m.start(1)] + body_new + s[m.end(1):]

# 3) убедимся, что декораторы — через router
s = re.sub(r'(?m)^(\s*)@dp\.(message|callback_query)\(', r'\1@router.\2(', s)

# Запись + бэкап
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: шаг выбора формата добавлен, set_gender теперь зовёт ask_format, регистрация на router.")
