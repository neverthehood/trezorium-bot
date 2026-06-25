# fix_strip_orphan_and_rank_handlers.py — убирает "висящие" print/await и хэндлеры best/worst
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализация невидимых + табов
s = (s.replace("\","")
       .replace("\ "," ")
       .replace("\r","")
       .replace("\t","    "))

# 1) Удалить осиротевший блок "print(...) / await dp.start_polling(bot)" перед if __main__
s = re.sub(
    r'(?ms)^\s+print\("Bot is starting\.\.\."\)\s*\n\s+await\s+dp\.start_polling\(bot\)\s*\n(?=^if\s+__name__\s*==)',
    '', s, flags=re.M
)

# 2) Вырезать целиком хэндлеры best:/worst:
for key in ("best", "worst"):
    pat = re.compile(
        rf'(?ms)^@dp\.callback_query\(F\.data\.startswith\("{key}:"\)\)\s*'
        rf'async\s+def\s+\w+\s*\([^)]*\)\s*:\s*.*?'
        rf'(?=^@dp\.callback_query|^@router\.callback_query|^async\s+def|^def|^class|\Z)', re.M)
    s = pat.sub('', s)

# 3) Выровнять декораторы и следующий за ними def на нулевой отступ
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
s = ''.join(out)

# 4) Перестроить хвост if __main__ на всякий случай
s = re.sub(r'(?ms)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*.*\Z',
           'if __name__ == "__main__":\n'
           '    import asyncio\n'
           '    print("Bot is starting...")\n'
           '    asyncio.run(main())\n',
           s)

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: удалил осиротевшие строки, best/worst хэндлеры; отступы нормализованы (backup: src/main.py.bak).")
