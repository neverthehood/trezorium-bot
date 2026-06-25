# fix_final_main_indent_and_set_aud.py — чинит обработчик aud: и блок запуска
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# 0) Нормализация невидимых и табов
s = (s.replace("\","")
       .replace("\ "," ")
       .replace("\r","")
       .replace("\t","    "))

# 1) Удалим "осиротевшую" заглушку под декоратором aud: и вставим корректный set_aud
pat_aud_block = re.compile(
    r'(?ms)^@dp\.callback_query\(F\.data\.startswith\("aud:"\)\)\s*'
    r'async\s+def\s+\w+\s*\([^)]*\)\s*:\s*.*?'
    r'(?=^@dp\.callback_query|^@router\.callback_query|^async\s+def|^def|^class|\Z)', re.M
)

new_set_aud = (
    '@dp.callback_query(F.data.startswith("aud:"))\n'
    'async def set_aud(cb: CallbackQuery):\n'
    '    _, val = cb.data.split(":", 1)\n'
    '    st = st_for(cb.message.chat.id)\n'
    '    st.mode = val if val in ("child","teen","adult") else "teen"\n'
    '    await safe_answer(cb, "Ок")\n'
    '    await cb.message.answer("Укажи пол.", reply_markup=kb_gender())\n'
    '\n'
)

s = pat_aud_block.sub(new_set_aud, s)

# 2) Приведём к нулевому отступу все декораторы и следующие за ними заголовки функций
lines = s.splitlines(True)
out = []
last_was_decorator = False
for ln in lines:
    if re.match(r'^\s*@(?:dp|router)\.', ln):
        ln = ln.lstrip()
        last_was_decorator = True
    elif re.match(r'^\s*(?:async\s+def|def)\s+\w+\s*\(', ln) and last_was_decorator:
        ln = ln.lstrip()
        last_was_decorator = False
    else:
        if ln.strip():
            last_was_decorator = False
    out.append(ln)
s = "".join(out)

# 3) Пересоберём нижний блок запуска (чтобы не было «пляшущих» отступов)
pat_main = re.compile(r'(?ms)^if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*.*\Z')
s = pat_main.sub(
    'if __name__ == "__main__":\n'
    '    import asyncio\n'
    '    print("Bot is starting...")\n'
    '    asyncio.run(main())\n',
    s
)

p.write_text(s, encoding="utf-8")
print("OK: set_aud починен, отступы выровнены, блок запуска нормализован.")
