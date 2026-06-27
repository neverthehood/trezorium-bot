import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Строка 633 (индекс 632) — дубликат if in_daily_mode: — удаляем
# Но сначала нужно убедиться, что это дубликат
if '        if in_daily_mode:' in lines[632]:
    print(f"Line 633 (idx 632) is duplicate: {repr(lines[632].rstrip())}")
    # Не удаляем, а проверяем — строка 632 уже правильная '    if in_daily_mode:'
    # Строка 633 (idx 632) — это дубликат, удаляем
    # Но индекс 632 — это строка 633
    pass

# Удаляем дубликат строки 633 (индекс 632) — это второй if in_daily_mode:
# Проверим: строка 631 (idx 630) — пустая, строка 632 (idx 631) — правильный if
# Строка 633 (idx 632) — дубликат if с 8 пробелами
# На самом деле строка 633 имеет индекс 632
print(f"Line 631 (idx 630): {repr(lines[630].rstrip())}")
print(f"Line 632 (idx 631): {repr(lines[631].rstrip())}")
print(f"Line 633 (idx 632): {repr(lines[632].rstrip())}")

# Ага! lines[632] (строка 633) — дубликат '        if in_daily_mode:'
# Удаляем его
del lines[632]

# Теперь нужно исправить блок try-except строки 650-654 (сдвинулись индексы на 1)
# Строка 650 (индекс 649?) — try с 20 пробелами, надо 16  
# Строка 651 — await с 24 пробелами, надо 20
# Строка 652 — print с 16, надо 20
# Строка 653 — except с 12, надо 16

# Находим try:
for i, line in enumerate(lines):
    if '                    try:' in line:
        print(f"Found try: at line {i}")
        lines[i] = '                try:\n'
        if i+1 < len(lines) and '                        await save_result' in lines[i+1]:
            lines[i+1] = '                    await save_result(cb.message.chat.id, code, st.vectors, raw_mods, gender=gender, age=age, looking_for=looking_for)\n'
        if i+2 < len(lines) and '                print(f' in lines[i+2]:
            lines[i+2] = '                    print(f"[DB] Daily result saved: {st.daily_next_index}/48")\n'
        if i+3 < len(lines) and '            except Exception' in lines[i+3]:
            lines[i+3] = '                except Exception as e:\n'
        if i+4 < len(lines) and '                print(f' in lines[i+4]:
            lines[i+4] = '                    print(f"[DB] Daily save error: {e}")\n'
        break

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
