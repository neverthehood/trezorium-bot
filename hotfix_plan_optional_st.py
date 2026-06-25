# hotfix_plan_optional_st.py — делает _plan_and_start(m, st=None) с безопасными дефолтами
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

block = (
    "def _plan_and_start(m, st=None):\n"
    "    \"\"\"Планирует маршрут по выбранному объёму (express/standard/deep) и режимам.\n"
    "    Если st не передан, берём состояние по chat.id.\"\"\"\n"
    "    if st is None:\n"
    "        st = st_for(m.chat.id)\n"
    "    # объём → количество вопросов\n"
    "    length = getattr(st, 'length', 'standard') or 'standard'\n"
    "    sample_map = {'express': 12, 'standard': 24, 'deep': 40}\n"
    "    sample_n = sample_map.get(length, 24)\n"
    "    # режимы по умолчанию на случай пустых значений\n"
    "    st.mode = getattr(st, 'mode', 'teen') or 'teen'\n"
    "    st.style = getattr(st, 'style', 'classic') or 'classic'\n"
    "    # собираем маршрут; при ошибке — мягкий откат\n"
    "    try:\n"
    "        st.route_core = build_route(sample_n, m.chat.id, st.mode, st.style)\n"
    "    except Exception:\n"
    "        st.route_core = build_route(min(10, sample_n), m.chat.id, st.mode, st.style)\n"
    "    return \"Начинаем!\"\n"
    "\n"
)

# заменить существующую _plan_and_start или вставить перед set_length
pat = re.compile(r'(?ms)^\s*def\s+_plan_and_start\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
if pat.search(s):
    s = pat.sub(block, s)
else:
    m = re.search(r'(?m)^\s*async\s+def\s+set_length\s*\(', s)
    s = s[:m.start()] + block + s[m.start():] if m else s.rstrip()+"\n\n"+block

# убедимся, что есть импорт build_route
if "build_route" not in s:
    s = s.replace("from .question_loader import", "from .question_loader import build_route,")
    if "build_route" not in s:
        s = s.replace("from .question_loader import load_catalog", "from .question_loader import load_catalog, build_route")

pathlib.Path("src/main.py").write_text(s, encoding="utf-8")
print("OK: _plan_and_start теперь принимает st=None и сам его берёт при необходимости.")
