# fix_unify_plan_and_start.py — удаляет дубликаты и вставляет устойчивую _plan_and_start
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    ")

# 1) Удаляем ВСЕ существующие определения _plan_and_start
pat_fun = re.compile(r'(?ms)^\s*def\s+_plan_and_start\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
while True:
    m = pat_fun.search(s)
    if not m: break
    s = s[:m.start()] + s[m.end():]

# 2) Убедимся, что импорт build_route есть
if "build_route" not in s:
    if "from .question_loader import" in s:
        s = s.replace("from .question_loader import", "from .question_loader import build_route,")
    else:
        # вставим рядом с другими импортами
        s = re.sub(r'(?m)^(from aiogram .*?\n)', r'\1from .question_loader import build_route\n', s, count=1)

# 3) Стабильная версия _plan_and_start: принимает Message ИЛИ CallbackQuery, st — опционально
block = (
    "def _plan_and_start(m, st=None):\n"
    "    \"\"\"Планирует маршрут по выбранному объёму и режимам.\n"
    "    m — Message ИЛИ CallbackQuery; st — SessionState или None.\"\"\"\n"
    "    # Достаём Message и chat_id из Message либо из CallbackQuery\n"
    "    msg = getattr(m, 'message', m)\n"
    "    chat = getattr(msg, 'chat', None)\n"
    "    chat_id = getattr(chat, 'id', None)\n"
    "    if st is None:\n"
    "        if chat_id is None:\n"
    "            raise RuntimeError('Нет chat_id для выбора сессии')\n"
    "        st = st_for(chat_id)\n"
    "    # Объём → количество вопросов\n"
    "    length = getattr(st, 'length', 'standard') or 'standard'\n"
    "    sample_map = {'express': 12, 'standard': 24, 'deep': 40}\n"
    "    sample_n = sample_map.get(length, 24)\n"
    "    # Режимы по умолчанию\n"
    "    st.mode = getattr(st, 'mode', 'teen') or 'teen'\n"
    "    st.style = getattr(st, 'style', 'classic') or 'classic'\n"
    "    # Планируем маршрут\n"
    "    if chat_id is None:\n"
    "        chat_id = msg.chat.id\n"
    "    st.route_core = build_route(sample_n, chat_id, st.mode, st.style)\n"
    "    return 'Начинаем!'\n"
    "\n"
)

# 4) Вставим новую функцию прямо перед set_length (если есть), иначе — в конец
m_setlen = re.search(r'(?m)^\s*async\s+def\s+set_length\s*\(', s)
if m_setlen:
    s = s[:m_setlen.start()] + block + s[m_setlen.start():]
else:
    s = s.rstrip() + "\n\n" + block

pathlib.Path("src/main.py").write_text(s, encoding="utf-8")
print("OK: _plan_and_start унифицирована и устойчива к Message/CallbackQuery; дубликаты удалены.")
