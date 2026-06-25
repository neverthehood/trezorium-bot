# hard_align_router_handlers_and_debug.py — сводим все хэндлеры к router и добавляем лог в set_length
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = (s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    "))

# 1) Импорт Router и router = Router()
if "from aiogram import Bot, Dispatcher, F, Router" not in s:
    s = s.replace("from aiogram import Bot, Dispatcher, F", "from aiogram import Bot, Dispatcher, F, Router")
if not re.search(r'(?m)^\s*router\s*=\s*Router\(\)\s*$', s):
    s = re.sub(r'(?m)^(from aiogram .*?\n)', r'\1router = Router()\n', s, count=1)

# 2) Все декораторы @dp.* -> @router.*
s = re.sub(r'(?m)^(\s*)@dp\.(message|callback_query)\(', r'\1@router.\2(', s)

# 3) Удаляем дубликаты set_aud (оставляем тот, что сразу под декоратором)
defs = list(re.finditer(r'(?m)^async\s+def\s+set_aud\s*\(', s))
if len(defs) > 1:
    keeps = []
    for m in defs:
        start = m.start()
        above = s[:start].splitlines()
        trail = "\n".join(above[-3:]) if above else ""
        if 'callback_query(F.data.startswith("aud:"))' in trail:
            keeps.append(m.start())
    keep_start = keeps[0] if keeps else defs[0].start()
    # вырезаем остальные
    spans = []
    for m in defs:
        if m.start() == keep_start:
            continue
        body = re.search(r'(?ms)(?=^\s*(?:async\s+def|def|@|class)\b|\Z)', s[m.end():])
        end = m.end() + (body.start() if body else 0)
        spans.append((m.start(), end))
    for a,b in reversed(spans):
        s = s[:a] + s[b:]

# 4) Добавляем диагностический лог в set_length
#    Вставим печать после вычисления st.length и перед вызовом _plan_and_start; а также после — размер маршрута.
pat_len = re.compile(r'(?ms)^@router\.callback_query\(F\.data\.startswith\("len:"\)\)\s*?\n\s*async\s+def\s+set_length\s*\([^)]*\)\s*:\s*(.*?)\n(?=\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z)', re.M)
m = pat_len.search(s)
if m:
    body = m.group(1)
    # добавим вставки, если их ещё нет
    if "DEBUG set_length" not in body:
        body_new = body
        # после присвоения st.length вставим print
        body_new = re.sub(
            r'(st\.length\s*=\s*val[^\n]*\n\s*await\s+safe_answer[^\n]*\n)',
            r'\1        print(f"[DEBUG] set_length: length={st.length} mode={getattr(st, \"mode\", None)} style={getattr(st, \"style\", None)}")\n',
            body_new, count=1)
        # после intro = _plan_and_start... вставим print про размер маршрута (если удастся)
        body_new = re.sub(
            r'(intro\s*=\s*_plan_and_start\(cb\.message,\s*st\)\s*\n)',
            r'\1        print(f"[DEBUG] route size: {len(getattr(st, \"route_core\", []) or [])}")\n',
            body_new, count=1)
        s = s[:m.start(1)] + body_new + s[m.end(1):]

# 5) Хвост запуска — оставим аккуратный
s = re.sub(r'(?ms)^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:\s*.*\Z',
           'if __name__ == "__main__":\n'
           '    import asyncio\n'
           '    asyncio.run(main())\n', s)

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: декораторы переведены на router, дубликаты set_aud убраны, лог set_length добавлен (backup: src/main.py.bak).")
