# fix_send_report_single.py — оставляет одну отправку HTML и убирает текстовые "фолбэки"
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# нормализуем невидимые символы и табы
s = (s.replace("\","")
       .replace("\ "," ")
       .replace("\r","")
       .replace("\t","    "))

# достаём тело finish_and_report
pat_fun = re.compile(r'(?ms)^(\s*)async\s+def\s+finish_and_report\s*\([^)]*\)\s*:\s*(.*?)\n(?=^\s*(?:async\s+def|def|@|class)\b|\Z)', re.M)
m = pat_fun.search(s)
if not m:
    raise SystemExit("finish_and_report() не найден")
indent, body = m.group(1), m.group(2)

# 1) убираем любые отправки "кусочков" текста html
body = re.sub(r'^\s*await\s+m\.answer\(.{0,120}?html\[?:?3900\].*?\)\s*$', "", body, flags=re.M)

# 2) удалим лишние answer_document(...) в этой функции (оставим только один позже)
body = re.sub(r'^\s*await\s+m\.answer_document\(.*?\)\s*$', "", body, flags=re.M)

# 3) гарантируем запись файла и ровно одну отправку документа
if "render_html_report(" in body:
    # если нет сохранения на диск — добавим
    if "reports_dir" not in body or "FSInputFile" not in body:
        add = (
            '\n'
            f'{indent}    # сохранить HTML и отправить одним документом\n'
            f'{indent}    import time, pathlib\n'
            f'{indent}    reports_dir = pathlib.Path("data/reports"); reports_dir.mkdir(parents=True, exist_ok=True)\n'
            f'{indent}    fname = f"report_{m.chat.id}_{int(time.time())}.html"\n'
            f'{indent}    fpath = reports_dir / fname\n'
            f'{indent}    fpath.write_text(html, encoding="utf-8")\n'
            f'{indent}    from aiogram.types import FSInputFile\n'
            f'{indent}    await m.answer_document(FSInputFile(fpath, filename=fname), caption="Полная версия отчёта (HTML)")\n'
        )
        body = re.sub(r'(html\s*=\s*render_html_report\([^)]*\)\s*)\n', r'\1' + add, body, count=1)

# вернуть в текст
s = s[:m.start(2)] + body + s[m.end(2):]

# записать с бэкапом
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: finish_and_report — одна отправка файла, без текстовых фолбэков.")
