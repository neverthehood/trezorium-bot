# fix_safe_answer_recursion.py — чинит safe_answer в src/main.py
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8")

# 1) гарантируем импорты
if "from aiogram.exceptions import TelegramBadRequest" not in s:
    s = s.replace(
        "from aiogram import Bot, Dispatcher, F",
        "from aiogram import Bot, Dispatcher, F\nfrom aiogram.exceptions import TelegramBadRequest",
        1
    )
if "from typing import Optional" not in s:
    s = s.replace(
        "from aiogram import Bot, Dispatcher, F",
        "from typing import Optional\nfrom aiogram import Bot, Dispatcher, F",
        1
    )

# 2) новый текст функции (без рекурсии, с поддержкой Py3.9)
new_fun = """
async def safe_answer(cb, text: Optional[str] = None):
    \"\"\"Аккуратно подтверждает нажатие инлайн-кнопки.
    Гасит TelegramBadRequest: query is too old/invalid id.\"\"\"
    try:
        if text is None:
            await cb.answer()
        else:
            await cb.answer(text)
    except TelegramBadRequest:
        pass

"""

# 3) вырежем старую safe_answer целиком и вставим новую
m = re.search(r"async\\s+def\\s+safe_answer\\s*\\(.*?\\):", s, flags=re.DOTALL)
if m:
    start = m.start()
    # ищем начало следующей функции def/async def
    n = re.search(r"^\\s*(?:def|async\\s+def)\\s+\\w+\\s*\\(", s[m.end():], flags=re.MULTILINE)
    if n:
        end = m.end() + n.start()
    else:
        end = len(s)
    s = s[:start] + new_fun + s[end:]
else:
    # если не нашли — просто добавим перед первым next_in_route/finish_and_report
    anchor = "def next_in_route" if "def next_in_route" in s else "async def main"
    s = s.replace(anchor, new_fun + anchor, 1)

p.write_text(s, encoding="utf-8")
print("OK: safe_answer переписана без рекурсии и с Optional[str].")
