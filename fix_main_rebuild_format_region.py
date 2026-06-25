# fix_main_rebuild_format_region.py — переcобирает блок выбора формата (kb_format, ask_format, set_format)
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализация скрытых символов
s = s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    ")

# Найдём начало функции set_aud — сюда будем "пришивать" корректный блок формата
m_aud = re.search(r'(?m)^async\s+def\s+set_aud\s*\([^)]*\)\s*:', s)
if not m_aud:
    raise SystemExit("Не нашёл set_aud — остановился, чтобы не повредить файл.")

# Границы того, что будем заменять: от kb_format (если есть) или ask_format — до set_aud
m_kb  = re.search(r'(?m)^def\s+kb_format\s*\(\)\s*:', s)
m_ask = re.search(r'(?m)^async\s+def\s+ask_format\s*\([^)]*\)\s*:', s)

start = None
if m_kb:  start = m_kb.start()
elif m_ask: start = m_ask.start()
else:
    # если ни kb_format, ни ask_format нет — вставим блок просто перед set_aud
    start = m_aud.start()

end = m_aud.start()

# Собираем эталонный блок целиком
block = (
"def kb_format():\n"
"    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B\n"
"    return InlineKeyboardMarkup(inline_keyboard=[\n"
"        [B(text=\"Классика\", callback_data=\"fmt:classic\")],\n"
"        [B(text=\"Истории\",  callback_data=\"fmt:story\")],\n"
"    ])\n"
"\n"
"async def ask_format(m, st):\n"
"    txt = (\"Выбери формат вопросов:\\n\\n\"\n"
"           \"• Классика — короткие, чёткие ситуации.\\n\"\n"
"           \"• Истории — развернутые мини-сюжеты с погружением.\")\n"
"    await m.answer(txt, reply_markup=kb_format())\n"
"\n"
"async def set_format(cb, st):\n"
"    # cb.data = fmt:classic|story\n"
"    st.style = cb.data.split(\":\")[1]\n"
"    await safe_answer(cb, \"Ок\")\n"
"    await ask_volume(cb.message, st)\n"
"\n"
)

# Вырезаем всё между start..end и вставляем эталон
s = s[:start] + block + s[end:]

# Страховка: удалим возможные «осиротевшие» четыре строки вне функций
s = re.sub(
    r'(?ms)^\s*#\s*cb\.data\s*=\s*fmt:classic\|story\s*\n'
    r'\s*st\.style\s*=\s*cb\.data\.split\(":\"\)\[1\]\s*\n'
    r'\s*await\s+safe_answer\(cb,\s*".*?"\)\s*\n'
    r'\s*await\s+ask_volume\(cb\.message,\s*st\)\s*\n', "", s)

# Зарегистрируем хэндлер формата (если вдруг не прописан)
if "F.data.startswith('fmt:')" not in s:
    s = s.replace("router.callback_query.register(set_volume",
                  "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

# На всякий добавим команду /format (можно менять режим на лету)
if not re.search(r'(?m)^@router\.message\(F\.text\.regexp\(\r?\'\^/format\$\',?\)?\)\s*', s):
    s += (
        "\n@router.message(F.text.regexp(r'^/format$'))\n"
        "async def cmd_format(m, state):\n"
        "    st = await state.get_data() or {}\n"
        "    class Obj: pass\n"
        "    o = Obj(); o.__dict__.update(st)\n"
        "    await ask_format(m, o)\n"
    )

p.write_text(s, encoding="utf-8")
print('OK: блок формата (kb_format/ask_format/set_format) перестроен и вставлен перед set_aud.')
