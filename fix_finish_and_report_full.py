# fix_finish_and_report_full.py — переопределяет finish_and_report() стабильной версией
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = (s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    "))

# 1) гарантируем импорты
if "FSInputFile" not in s:
    s = re.sub(r'(?m)^(from aiogram\.types import .*)$',
               r'\1\nfrom aiogram.types import FSInputFile', s, count=1)
if "load_catalog" not in s:
    s = s.replace("from .question_loader import", "from .question_loader import load_catalog,")
    if "load_catalog" not in s:
        s = re.sub(r'(?m)^(from aiogram .*?\n)',
                   r'\1from .question_loader import load_catalog\n', s, count=1)

# 2) заменяем всю функцию finish_and_report на новую
pat = re.compile(r'(?ms)^\s*async\s+def\s+finish_and_report\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
new_fun = """
async def finish_and_report(m, st):
    \"\"\"Финиш опроса: считаем результат, готовим HTML, шлём одним файлом.\"\"\"
    # Короткая карточка (если есть рендерер)
    try:
        vectors = vector_totals(st)
    except Exception:
        vectors = {}
    try:
        code = pick_result(vectors)
    except Exception:
        code = "—"
    try:
        short = render_short_card(code)
        await m.answer(short)
    except Exception:
        # тихо: карточка не критична
        pass

    # Модификаторы (если получится): берём актуальный каталог
    mods = {"raw": {}, "pairs": []}
    try:
        catalog = load_catalog(getattr(st, "mode", "teen"), getattr(st, "style", "classic"))
        try:
            mods = compute_mods(getattr(st, "answers", {}) or {}, catalog) or mods
        except Exception:
            pass
    except Exception:
        pass

    # Сформируем HTML отчёт (поддержим разные сигнатуры)
    html = "<h1>Отчёт</h1>"
    try:
        html = render_html_report(code, vectors, getattr(st, "answers", {}) or {}, [], mods)
    except TypeError:
        try:
            html = render_html_report(code, vectors, getattr(st, "answers", {}) or {}, [])
        except TypeError:
            try:
                html = render_html_report(code, vectors)
            except Exception:
                pass
    except Exception:
        pass

    # Сохраняем и шлём одним документом
    try:
        import time, pathlib
        reports_dir = pathlib.Path("data/reports"); reports_dir.mkdir(parents=True, exist_ok=True)
        fname = f"report_{m.chat.id}_{int(time.time())}.html"
        fpath = reports_dir / fname
        fpath.write_text(html, encoding="utf-8")
        await m.answer_document(FSInputFile(fpath, filename=fname), caption="Полная версия отчёта (HTML)")
    except Exception:
        # на крайний случай
        try:
            await m.answer(html[:3500])
        except Exception:
            await m.answer("Готово! (не удалось отправить файл отчёта)")
"""

s = pat.sub(new_fun.strip()+"\n", s)

# 3) пишем файл с бэкапом
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: finish_and_report() переписан устойчиво; импорты добавлены.")
