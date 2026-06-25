# fix_add_plan_and_start.py — добавляет отсутствующую функцию _plan_and_start
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

if not re.search(r'(?m)^\s*def\s+_plan_and_start\s*\(', s):
    block = (
        "def _plan_and_start(m, st):\n"
        "    # Определяем объём по выбору пользователя\n"
        "    length = (getattr(st, 'length', None) or 'standard')\n"
        "    if length == 'express':\n"
        "        sample_n = 10\n"
        "    elif length == 'deep':\n"
        "        sample_n = 40\n"
        "    else:\n"
        "        sample_n = 20\n"
        "    # Собираем маршрут из банка вопросов\n"
        "    st.route_core = build_route(sample_n, m.chat.id, st.mode, st.style)\n"
        "    return 'Начинаем!'\n"
        "\n"
    )
    # Вставим блок прямо перед set_length (если она есть), иначе — в конец файла
    m = re.search(r'(?m)^\s*async\s+def\s+set_length\s*\(', s)
    if m:
        s = s[:m.start()] + block + s[m.start():]
    else:
        s = s.rstrip() + "\n\n" + block
    p.write_text(s, encoding="utf-8")
    print("OK: добавил _plan_and_start() в src/main.py")
else:
    print("OK: _plan_and_start() уже существует — ничего не менял.")
