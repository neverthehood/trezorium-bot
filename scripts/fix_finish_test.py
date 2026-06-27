import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Заменяем строки 140-155 (индексы 139-154) на правильные
new_lines = [
    '    # Сохраняем\n',
    '    print(f"[DB] Save user {m.chat.id}...")\n',
    '    raw_gender = getattr(st, "gender", "")\n',
    '    gender = "M" if raw_gender == "male" else "F" if raw_gender == "female" else ""\n',
    '    age = getattr(st, "age", 0)\n',
    '    looking_for = getattr(st, "looking_for", "") or ""\n',
    '    try:\n',
    '        u = await save_user(m.chat.id, m.from_user.username, gender=gender, age=age, looking_for=looking_for)\n',
    '        print(f"[DB] User saved: {u}")\n',
    '    except Exception as e:\n',
    '        print(f"[DB] User save error: {e}")\n',
    '    try:\n',
    '        r = await save_result(m.chat.id, code, st.vectors, raw_mods, gender=gender, age=age, looking_for=looking_for)\n',
    '        print(f"[DB] Result saved: {r}")\n',
    '    except Exception as e:\n',
    '        print(f"[DB] Result save error: {e}")\n',
]

lines[139:155] = new_lines

# Строка 157 (индекс 156) — отступ
lines[156] = '    # Отложенный поиск мэтча (через 24 часа)\n'

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
