# fix_send_report_single_v2.py — одна отправка HTML-отчёта (исправленная версия)
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = (s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    "))

pat_fun = re.compile(r'(?ms)^(\s*)async\s+def\s+finish_and_report\s*\([^)]*\)\s*:\s*(.*?)\n(?=^\s*(?:async\s+def|def|@|class)\b|\Z)', re.M)
m = pat_fun.search(s)
if not m:
    raise SystemExit("finish_and_report() не найден")
indent, body = m.group(1), m.group(2)

# 1) убрать текстовые куски html
body = re.sub(r'^\s*await\s+m\.answer\(.{0,200}?html\[?:?3900\].*?\)\s*$', "", body, flags=re.M)
# 2) убрать все предыдущие answer_document(...) в этой функции
body = re.sub(r'^\s*await\s+m\.answer_document\(.*?\)\s*$', "", body, flags=re.M)

# 3) добавить запись файла и одну отправку документа
if "render_html_report(" in body and "reports_dir" not in body:
    add = (
        "\n"
        + indent + "    # сохранить HTML и отправить одним документом\n"
        + indent + "    import time, pathlib\n"
        + indent + "    reports_dir = pathlib.Path(\"data/reports\"); reports_dir.mkdir(parents=True, exist_ok=True)\n"
        + indent + "    fname = f\"report_{m.chat.id}_{int(time.time())}.html\"\n"
        + indent + "    fpath = reports_dir / fname\n"
        + indent + "    fpath.write_text(html, encoding=\"utf-8\")\n"
        + indent + "    from aiogram.types import FSInputFile\n"
        + indent + "    await m.answer_document(FSInputFile(fpath, filename=fname), caption=\"Полная версия отчёта (HTML)\")\n"
    )
    body = re.sub(r'(html\s*=\s*render_html_report\([^)]*\)\s*)\n', r'\1' + add, body, count=1)

s = s[:m.start(2)] + body + s[m.end(2):]

shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: finish_and_report — теперь одна отправка файла, без текстовых фолбэков.")
