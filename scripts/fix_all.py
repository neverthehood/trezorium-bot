import sys, re
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Фикс if in_daily_mode: (8 -> 4 пробела)
content = content.replace(
    '        if in_daily_mode:\n            # Режим daily',
    '    if in_daily_mode:\n        # Режим daily'
)

# 2. Фикс try: (24 -> 20 пробелов?) Найдём точное вхождение
# Ищем: looking_for = ... \n                        try:
content = re.sub(
    r"(looking_for = getattr\(st, 'looking_for', ''\) or '')\n +try:",
    r"\1\n                    try:",
    content
)

# 3. Фикс await save_result (ниже try)
content = re.sub(
    r"( +)try:\n +await save_result",
    r"\1try:\n\1    await save_result",
    content
)

# 4. Фикс commands = [ (8 -> 4 пробела)
content = content.replace(
    'async def set_commands(bot):\n        commands = [',
    'async def set_commands(bot):\n    commands = ['
)

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
