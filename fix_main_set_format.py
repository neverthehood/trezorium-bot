# fix_main_set_format.py — чинит set_format и подключает mods к отчёту
import re, pathlib
p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8")

# Импорт вычисления модификаторов
if "from .mods import compute_mods" not in s:
    s = s.replace("from .engine import apply_weights, pick_result, vector_totals",
                  "from .engine import apply_weights, pick_result, vector_totals\nfrom .mods import compute_mods", 1)

# Функция set_format
pat = re.compile(r"async\s+def\s+set_format\s*\([^)]*\)\s*:\s*[\s\S]*?(?=^\s*(?:async\s+def|def|@|class)\b)", re.MULTILINE)
new_fun = (
"async def set_format(cb, st):\n"
"    # cb.data = fmt:classic|story\n"
"    st.style = cb.data.split(\":\")[1]\n"
"    await safe_answer(cb, \"Ок\")\n"
"    await ask_volume(cb.message, st)\n\n"
)
if pat.search(s):
    s = pat.sub(new_fun, s)
else:
    s = s.replace("async def set_aud", new_fun + "async def set_aud", 1)

# Регистрация хэндлера
if "F.data.startswith('fmt:')" not in s:
    s = s.replace("router.callback_query.register(set_volume",
                  "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

# После подсчёта векторов — посчитать модификаторы
s = re.sub(r"(vectors\s*=\s*vector_totals\(.*?\)\s*)\n", r"\1\n    mods = compute_mods(st.answers, bank)\n", s, flags=re.DOTALL)

# Передать mods в отчёт
s = re.sub(r"render_html_report\(\s*code\s*,\s*vectors\s*,\s*features\s*,\s*neighbors\s*\)",
           "render_html_report(code, vectors, features, neighbors, mods)", s)

p.write_text(s, encoding="utf-8")
print("OK: main.py — set_format исправлен, mods считаются и передаются.")
