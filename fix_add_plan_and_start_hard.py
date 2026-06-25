# fix_add_plan_and_start_hard.py — добавляет _plan_and_start и импорт build_route
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = s.replace("\","").replace("\ "," ").replace("\r","")

# 1) Если нет импорта build_route — добавим после первых импортов aiogram
if "build_route" not in s:
    s = re.sub(
        r'(?m)^(from\s+aiogram[^\n]*\n)',
        r'\1from .question_loader import build_route\n',
        s, count=1
    )

# 2) Вставим/заменим функцию _plan_and_start
block = (
    "def _plan_and_start(m, st):\n"
    "    \"\"\"Планирует маршрут по выбранному объёму и режимам, возвращает текст-вступление.\"\"\"\n"
    "    length = getattr(st, 'length', 'standard') or 'standard'\n"
    "    # Кол-во вопросов можно подстроить при желании\n"
    "    sample_map = {'express': 12, 'standard': 24, 'deep': 40}\n"
    "    sample_n = sample_map.get(length, 24)\n"
    "    # Собираем маршрут (аудитория: st.mode; формат: st.style)\n"
    "    st.route_core = build_route(sample_n, m.chat.id, st.mode, st.style)\n"
    "    return \"Начинаем!\"\n"
    "\n"
)

pat = re.compile(r'(?ms)^\s*def\s+_plan_and_start\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
if pat.search(s):
    s = pat.sub(block, s)
else:
    m = re.search(r'(?m)^\s*async\s+def\s+set_length\s*\(', s)
    s = s[:m.start()] + block + s[m.start():] if m else s.rstrip()+"\n\n"+block

p.write_text(s, encoding="utf-8")
print("OK: _plan_and_start добавлен, импорт build_route проверен.")
