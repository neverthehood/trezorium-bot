# fix_main_wipe_set_format_and_insert.py
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# 0) Глобальная нормализация файла: убрать BOM/NBSP/CR, табы → 4 пробела
s = s.replace("\","").replace("\ "," ")
s = s.replace("\r","")
s = s.replace("\t","    ")

# 1) Удаляем ВСЕ существующие определения set_format (какими бы они ни были)
pat = re.compile(r'(?ms)^async\s+def\s+set_format\s*\([^)]*\)\s*:\s*.*?(?=^async\s+def\b|^def\b|^@|^class\b|\Z)')
while True:
    m = pat.search(s)
    if not m: break
    s = s[:m.start()] + s[m.end():]

# 2) Готовим корректную функцию
new_fun = (
"async def set_format(cb, st):\n"
"    # cb.data = fmt:classic|story\n"
"    st.style = cb.data.split(\":\")[1]\n"
"    await safe_answer(cb, \"Ок\")\n"
"    await ask_volume(cb.message, st)\n"
"\n"
)

# 3) Вставляем после ask_format (если есть), иначе — в конец
ask_pat = re.compile(r'(?ms)^async\s+def\s+ask_format\s*\([^)]*\)\s*:\s*.*?\n\n')
m = ask_pat.search(s)
if m:
    s = s[:m.end()] + new_fun + s[m.end():]
else:
    s = s.rstrip() + "\n\n" + new_fun

# 4) Регистрируем обработчик, если ещё не зарегистрирован
if "F.data.startswith('fmt:')" not in s:
    s = s.replace("router.callback_query.register(set_volume",
                  "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

p.write_text(s, encoding="utf-8")
print("OK: set_format полностью перезаписан и файл нормализован.")
