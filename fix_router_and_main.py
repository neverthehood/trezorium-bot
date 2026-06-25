# fix_router_and_main.py — перевод декораторов на router и чинит main()
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализация невидимых символов и табов
s = (s.replace("\","").replace("\ "," ")
       .replace("\r","").replace("\t","    "))

# 1) Импорт Router
s = re.sub(r'from\s+aiogram\s+import\s+Bot,\s*Dispatcher,\s*F(?!,)',
           'from aiogram import Bot, Dispatcher, F, Router', s)

if 'from aiogram import Bot, Dispatcher, F, Router' not in s:
    # если не было исходной строки — добавим рядом с другими импортами aiogram
    s = s.replace('from aiogram import Bot, Dispatcher, F',
                  'from aiogram import Bot, Dispatcher, F, Router')

# 2) Глобальный router = Router()
if not re.search(r'(?m)^\s*router\s*=\s*Router\(\)\s*$', s):
    # вставим сразу после импортов aiogram
    s = re.sub(r'(?m)^(from aiogram .*?\n)',
               r'\1router = Router()\n', s, count=1)

# 3) Все декораторы @dp.* -> @router.*
s = re.sub(r'(?m)^(\s*)@dp\.(message|callback_query)\(', r'\1@router.\2(', s)

# 4) Удалить дубль set_aud, который без декоратора
# Оставляем только версию, непосредственно идущую за декоратором @router.callback_query("aud:")
def remove_duplicate_set_aud(text: str) -> str:
    # найдём все определения set_aud
    defs = list(re.finditer(r'(?m)^async\s+def\s+set_aud\s*\(', text))
    if len(defs) <= 1:
        return text
    # проверим, какой из них идет сразу после декоратора
    keep_spans = []
    for m in defs:
        start = m.start()
        # смотрим 2 строки выше — есть ли @router.callback_query(F.data.startswith("aud:"))
        above = text[:start].splitlines()
        trail = "\n".join(above[-3:]) if above else ""
        if 'callback_query(F.data.startswith("aud:"))' in trail:
            keep_spans.append((m.start(), m.end()))
    # оставим первый такой; остальные вырежем
    keep_idx = keep_spans[0][0] if keep_spans else defs[0].start()
    # вырежем все остальные блоки def set_aud до следующего def/async def/@/class
    out = text
    removes = []
    for m in defs:
        if m.start() == keep_idx:
            continue
        # границы блока
        tail = re.search(r'(?ms)(?=^\s*(?:async\s+def|def|@|class)\b|\Z)', out[m.end():])
        end = m.end() + (tail.start() if tail else 0)
        removes.append((m.start(), end))
    for a,b in reversed(removes):
        out = out[:a] + out[b:]
    return out

s = remove_duplicate_set_aud(s)

# 5) Перезаписать main() на корректный
pat_main_def = re.compile(r'(?ms)^async\s+def\s+main\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
s = pat_main_def.sub(
    'async def main():\n'
    '    from .config import cfg\n'
    '    bot = Bot(cfg.BOT_TOKEN)\n'
    '    dp = Dispatcher()\n'
    '    dp.include_router(router)\n'
    '    print("Bot is starting...")\n'
    '    await dp.start_polling(bot)\n'
, s)

# 6) Хвост запуска (__main__)
s = re.sub(r'(?ms)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*.*\Z',
           'if __name__ == "__main__":\n'
           '    import asyncio\n'
           '    asyncio.run(main())\n', s)

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: декораторы переведены на router, дубликат set_aud удалён, main() и запуск починены (backup: src/main.py.bak).")
