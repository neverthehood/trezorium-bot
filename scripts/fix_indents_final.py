import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Строка 325 (индекс 324) — welcome = ( с 16 пробелами -> 4
lines[324] = '    welcome = (\n'

# Строка 339 (индекс 338) — пустая с 1 пробелом -> пустая
lines[338] = '\n'

# Проверяем, что @router.message(CommandStart()) без дубликата
# Строки 322 и 323 (индексы 321, 322) — два декоратора
# Удаляем дубликат
idx = 322
if '@router.message(CommandStart())' in lines[idx]:
    del lines[idx]
    print(f'Deleted duplicate decorator at line {idx+1}')
else:
    print(f'No duplicate at line {idx+1}')

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
