# hotfix_no_double_intro.py
from pathlib import Path
import re

p = Path("src/main.py")
s = p.read_text(encoding="utf-8")

# (1) в set_length() убрать лишнее "Начинаем!"
s = re.sub(r'await\s+cb\.message\.answer\("Начинаем!"\)\s*\n', "", s, count=1)

# (2) сделать ответ _plan_and_start() осмысленным
s = re.sub(r'return\s+"Начинаем!"', 'return "Маршрут готов — поехали!"', s, count=1)

p.write_text(s, encoding="utf-8")
print("OK: убрано двойное «Начинаем!», интро осмысленное.")
