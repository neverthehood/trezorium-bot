# fix_main_docstring_ru.py — чинит единственную битую докстрингу у safe_answer()
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\","")

# найдём докстрингу сразу после объявления safe_answer(...)
m = re.search(r'(?ms)async\s+def\s+safe_answer\([^)]*\):\s*\n\s*("""[\s\S]*?""")', s)
if m:
    good = '"""Аккуратно подтверждает нажатие инлайн-кнопки."""'
    s = s[:m.start(1)] + good + s[m.end(1):]
    p.write_text(s, encoding="utf-8")
    print("OK: docstring у safe_answer() исправлена.")
else:
    print("Докстринга у safe_answer() не найдена — ничего не менял.")
