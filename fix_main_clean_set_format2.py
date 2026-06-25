# fix_main_clean_set_format2.py — тотальная чистка set_format + вставка корректного блока
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# 0) Нормализуем файл: убираем BOM/NBSP/CR, табы → 4 пробела
s = s.replace("\","").replace("\ "," ")
s = s.replace("\r","")
s = s.replace("\t","    ")

# 1) Удаляем все определения функции set_format целиком
pat_fun = re.compile(r'(?ms)^async\s+def\s+set_format\s*\([^)]*\)\s*:\s*.*?(?=^(?:async\s+def|def|@|class)\b|\Z)')
while True:
    m = pat_fun.search(s)
    if not m: break
    s = s[:m.start()] + s[m.end():]

# 2) Удаляем «осиротевший» 4-строчный блок, если он остался вне функции
pat_orphan = re.compile(
    r'(?ms)^\s*#\s*cb\.data\s*=\s*fmt:classic\|story\s*\n'
    r'\s*st\.style\s*=\s*cb\.data\.split\(":\"\)\[1\]\s*\n'
    r'\s*await\s+safe_answer\(cb,\s*".*?"\)\s*\n'
    r'\s*await\s+ask_volume\(cb\.message,\s*st\)\s*\n'
)
s = pat_orphan.sub("", s)

# 3) Формируем единственно верную функцию
new_fun = (
"async def set_format(cb, st):\n"
"    # cb.data = fmt:classic|story\n"
"    st.style = cb.data.split(\":\")[1]\n"
"    await safe_answer(cb, \"Ок\")\n"
"    await ask_volume(cb.message, st)\n"
"\n"
)

# 4) Вставляем её сразу после ask_format (если он есть), иначе в конец файла
pat_ask = re.compile(r'(?ms)^async\s+def\s+ask_format\s*\([^)]*\)\s*:\s*.*?\n\n')
m = pat_ask.search(s)
if m:
    s = s[:m.end()] + new_fun + s[m.end():]
else:
    s = s.rstrip() + "\n\n" + new_fun

# 5) Регистрируем хэндлер, если вдруг не добавлен
if "F.data.startswith('fmt:')" not in s:
    s = s.replace("router.callback_query.register(set_volume",
                  "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

p.write_text(s, encoding="utf-8")
print("OK: set_format очищен и вставлен корректно.")
