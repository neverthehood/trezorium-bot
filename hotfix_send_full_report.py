# hotfix_send_full_report.py — сохраняет HTML-отчёт и отправляет его как документ
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    ")

# 1) Добавим импорт FSInputFile, если его нет
if "from aiogram.types import FSInputFile" not in s:
    s = re.sub(r'(?m)^(from aiogram\.types import .*)$',
               r'\1\nfrom aiogram.types import FSInputFile', s, count=1)
    if "from aiogram.types import FSInputFile" not in s:
        # если не нашли строку с импортами типов — вставим рядом с другими импортами aiogram
        s = re.sub(r'(?m)^(from aiogram .*?\n)',
                   r'\1from aiogram.types import FSInputFile\n', s, count=1)

# 2) Внутри finish_and_report после строки с render_html_report — записать файл и отправить документом
pat_fun = re.compile(r'(?ms)^\s*async\s+def\s+finish_and_report\s*\([^)]*\)\s*:\s*(.*?)\n(?=^\s*(?:async\s+def|def|@|class)\b|\Z)', re.M)
m = pat_fun.search(s)
if not m:
    raise SystemExit("Не нашёл finish_and_report — проверь файл.")

body = m.group(1)

if "render_html_report" in body and "FSInputFile" not in body:
    body_new = re.sub(
        r'(html\s*=\s*render_html_report\([^)]*\)\s*)\n',
        r'\1\n'
        r'    # сохранить HTML и отправить как документ\n'
        r'    import time, os, pathlib\n'
        r'    reports_dir = pathlib.Path("data/reports"); reports_dir.mkdir(parents=True, exist_ok=True)\n'
        r'    fname = f"report_{m.chat.id}_{int(time.time())}.html"\n'
        r'    fpath = reports_dir / fname\n'
        r'    try:\n'
        r'        fpath.write_text(html, encoding="utf-8")\n'
        r'    except Exception:\n'
        r'        # на всякий случай создадим папку ещё раз и повторим\n'
        r'        reports_dir.mkdir(parents=True, exist_ok=True)\n'
        r'        fpath.write_text(html, encoding="utf-8")\n'
        r'    try:\n'
        r'        await m.answer_document(document=FSInputFile(fpath, filename=fname), caption="Полная версия отчёта во вложении.")\n'
        r'    except Exception as e:\n'
        r'        # Фоллбэк: отправим как текст (может обрезаться лимитом Telegram)\n'
        r'        try:\n'
        r'            await m.answer(html[:3900])\n'
        r'        except Exception:\n'
        r'            await m.answer("Не удалось отправить файл отчёта. Попробуй ещё раз позже.")\n',
        body,
        count=1
    )
    s = s[:m.start(1)] + body_new + s[m.end(1):]

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: finish_and_report теперь сохраняет HTML и шлёт документ.")
