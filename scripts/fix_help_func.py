import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ищем дубликат help_text = ( после h_start
import re

# Удаляем блок help_text = ( ... ) без декоратора (после h_start и перед @router.message(Command("daily")))
# Найдём шаблон: после await m.answer(welcome... идёт help_text = ( ... ) await m.answer(...)
pattern = r"(await m\.answer\(welcome, reply_markup=keyboard, parse_mode=\"Markdown\"\)\n)\n    help_text = \([\s\S]*?    await m\.answer\(help_text, parse_mode=\"Markdown\"\)"
replacement = r"\1"
content = re.sub(pattern, replacement, content)

# Вставляем правильную h_help после h_start
insert_marker = '    await m.answer(welcome, reply_markup=keyboard, parse_mode="Markdown")'

help_func = '''

@router.message(Command("help"))
async def h_help(m: Message):
    help_text = (
        "\\U0001f916 *Trezorium — команды*\\n\\n"
        "/start — начать тест\\n"
        "/profile — мой профиль\\n"
        "/agreement — пользовательское соглашение\\n"
        "/privacy — политика конфиденциальности\\n"
        "/delete_me — удалить данные\\n"
        "/help — эта подсказка"
    )
    await m.answer(help_text, parse_mode="Markdown")
'''

content = content.replace(insert_marker, insert_marker + help_func)

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
