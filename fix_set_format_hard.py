# fix_set_format_hard.py — переписывает set_format с правильными отступами и регистрирует хэндлер
import re, pathlib
p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

new_block = (
"async def set_format(cb, st):\n"
"    # cb.data = fmt:classic|story\n"
"    st.style = cb.data.split(\":\")[1]\n"
"    await safe_answer(cb, \"Ок\")\n"
"    await ask_volume(cb.message, st)\n"
"\n"
)

lines = s.splitlines(True)
start = None
for i, line in enumerate(lines):
    if re.match(r'^async\\s+def\\s+set_format\\b', line):
        start = i
        break

if start is not None:
    end = start + 1
    while end < len(lines):
        if re.match(r'^(async\\s+def|def\\s|@|class\\s)', lines[end]):
            break
        end += 1
    s2 = ''.join(lines[:start]) + new_block + ''.join(lines[end:])
else:
    m = re.search(r'^async\\s+def\\s+ask_format\\b[\\s\\S]*?\\n\\n', s, re.M)
    if m:
        s2 = s[:m.end()] + new_block + s[m.end():]
    else:
        s2 = s.rstrip() + "\\n\\n" + new_block

if "F.data.startswith('fmt:')" not in s2:
    s2 = s2.replace("router.callback_query.register(set_volume",
                    "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

p.write_text(s2, encoding="utf-8")
print("OK: set_format переписан жёстко.")
