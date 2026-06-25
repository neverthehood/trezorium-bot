# hotfix_cb_safe_answer.py — заменяет cb.answer на безопасный вариант
import pathlib, re

p = pathlib.Path("src/main.py")
src = p.read_text(encoding="utf-8")

# 1) импорт исключения
if "from aiogram.exceptions import TelegramBadRequest" not in src:
    src = src.replace(
        "from aiogram import Bot, Dispatcher, F",
        "from aiogram import Bot, Dispatcher, F\nfrom aiogram.exceptions import TelegramBadRequest",
        1
    )

# 2) вставка safe_answer() после константы LETTERS
if "def safe_answer(cb" not in src:
    insert_after = 'LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"'
    helper = """
async def safe_answer(cb, text: str | None = None):
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
    src = src.replace(insert_after, insert_after + "\n\n" + helper, 1)

# 3) заменить все вызовы cb.answer на safe_answer
src = re.sub(r"await\s+cb\.answer\(", "await safe_answer(cb, ", src)          # с текстом
src = re.sub(r"await\s+cb\.answer\(\)", "await safe_answer(cb)", src)          # без текста

p.write_text(src, encoding="utf-8")
print("OK: cb.answer → safe_answer(cb, ...) в src/main.py")
