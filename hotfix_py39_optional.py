# hotfix_py39_optional.py
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8")

# Добавим импорт Optional, если его нет
if "from typing import Optional" not in s:
    s = s.replace(
        "from aiogram import Bot, Dispatcher, F",
        "from typing import Optional\nfrom aiogram import Bot, Dispatcher, F",
        1
    )

# Заменим проблемную аннотацию параметра
s = re.sub(r"text:\s*str\s*\|\s*None", "text: Optional[str]", s)

p.write_text(s, encoding="utf-8")
print("OK: main.py теперь совместим с Python 3.9")
