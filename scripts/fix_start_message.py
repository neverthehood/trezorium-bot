import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Замена первого сообщения
content = content.replace(
    '👋 *Trezorium* — сокровищница твоей половинки.',
    '👋 *Трезориум* — в поисках сокровищ'
)

# 2. Удаление дубликата print
content = content.replace(
    '        print(f"[DB] Result save error: {e}")\n        print(f"[DB] Result save error: {e}")',
    '        print(f"[DB] Result save error: {e}")'
)

# 3. Удаление дубликата комментария
content = content.replace(
    '    # Отложенный поиск мэтча (через 24 часа)\n        # Отложенный поиск мэтча (через 24 часа)',
    '    # Отложенный поиск мэтча (через 24 часа)'
)

# 4. Добавляем определение in_daily_mode в ans
old_ans_block = '''    await safe_answer(cb)

    if in_daily_mode:'''
new_ans_block = '''    await safe_answer(cb)

    # Определяем режим
    in_daily_mode = getattr(st, 'daily_mode', False) and getattr(st, 'daily_asked', [])
    if in_daily_mode:'''
content = content.replace(old_ans_block, new_ans_block)

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
