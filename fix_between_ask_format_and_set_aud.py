# fix_between_ask_format_and_set_aud.py — чинит блок формата и отступы
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализация скрытых символов
s = s.replace("\","").replace("\ "," ")
s = s.replace("\r","").replace("\t","    ")

# Найдём границы: начало ask_format и начало set_aud
m_ask = re.search(r'(?m)^async\s+def\s+ask_format\s*\([^)]*\)\s*:\s*', s)
m_aud = re.search(r'(?m)^async\s+def\s+set_aud\s*\([^)]*\)\s*:\s*', s)

code_block = (
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

if m_ask and m_aud and m_ask.start() < m_aud.start():
    # Вырезаем всё между ask_format и set_aud и вставляем наш корректный блок
    start = m_ask.start()
    end   = m_aud.start()
    # Удалим весь «тело» ask_format+старые set_format/мусор до set_aud
    # Для надёжности подвинем start к началу строки
    while start > 0 and s[start-1] != "\n": start -= 1
    s = s[:start] + code_block + s[end:]
else:
    # Если не нашли оба — просто добавим наш блок в конец (не помешает)
    s = s.rstrip() + "\n\n" + code_block

# Удалим возможные «осиротевшие» 4 строки вне функции (иногда остаются после автопатчей)
s = re.sub(
    r'(?ms)^\s*#\s*cb\.data\s*=\s*fmt:classic\|story\s*\n'
    r'\s*st\.style\s*=\s*cb\.data\.split\(":\"\)\[1\]\s*\n'
    r'\s*await\s+safe_answer\(cb,\s*".*?"\)\s*\n'
    r'\s*await\s+ask_volume\(cb\.message,\s*st\)\s*\n', "", s)

# Зарегистрируем хэндлер формата, если вдруг пропал
if "F.data.startswith('fmt:')" not in s:
    s = s.replace("router.callback_query.register(set_volume",
                  "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

p.write_text(s, encoding="utf-8")
print("OK: блок ask_format/set_format перезаписан, отступы очищены.")
