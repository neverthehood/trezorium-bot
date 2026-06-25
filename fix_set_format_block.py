# fix_set_format_block.py — жёстко перезаписывает функцию set_format с правильными отступами
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

# заменить существующий блок или вставить после ask_format
pat = re.compile(r"async\\s+def\\s+set_format\\s*\\([^)]*\\)\\s*:\\s*[\\s\\S]*?(?=^\\s*(?:async\\s+def|def|@|class)\\b|\\Z)", re.M)
if pat.search(s):
    s = pat.sub(new_block, s)
else:
    pat2 = re.compile(r"async\\s+def\\s+ask_format\\s*\\([^)]*\\)\\s*:\\s*[\\s\\S]*?\\n\\n", re.M)
    if pat2.search(s):
        s = pat2.sub(lambda m: m.group(0) + new_block, s, count=1)
    else:
        s += "\\n\\n" + new_block

# зарегистрировать хэндлер, если вдруг нет
if "F.data.startswith('fmt:')" not in s:
    s = s.replace("router.callback_query.register(set_volume",
                  "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume", 1)

p.write_text(s, encoding="utf-8")
print("OK: set_format блок перезаписан корректно.")
