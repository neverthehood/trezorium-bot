import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Строка 647 (индекс 646) try: с 16 -> 12
lines[646] = '            try:\n'
# Строка 648 (индекс 647) await с 20 -> 16
lines[647] = '                await save_result(cb.message.chat.id, code, st.vectors, raw_mods, gender=gender, age=age, looking_for=looking_for)\n'
# Строка 649 (индекс 648) print с 20 -> 16
lines[648] = '                print(f"[DB] Daily result saved: {st.daily_next_index}/48")\n'
# Строка 650 (индекс 649) except с 16 -> 12
lines[649] = '            except Exception as e:\n'
# Строка 651 (индекс 650) print с 20 -> 16
lines[650] = '                print(f"[DB] Daily save error: {e}")\n'

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
