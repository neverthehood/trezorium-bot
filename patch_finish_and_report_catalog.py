# patch_finish_and_report_catalog.py  пробрасываем catalog в render_html_report
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализуем переводы строк
s = s.replace("\r","")

# Заменим любой вызов render_html_report(..., [], mods) или без mods  на передачу catalog
s = re.sub(
    r'render_html_report\(\s*code\s*,\s*vectors\s*,\s*[^,]+,\s*\[\s*\]\s*,\s*mods\s*\)',
    r'render_html_report(code, vectors, getattr(st,"answers",{}) or {}, catalog, mods)',
    s
)
s = re.sub(
    r'render_html_report\(\s*code\s*,\s*vectors\s*,\s*[^,]+,\s*\[\s*\]\s*\)',
    r'render_html_report(code, vectors, getattr(st,"answers",{}) or {}, catalog, {"raw":{}, "pairs":[]})',
    s
)
# Если вызывалось без 4-го аргумента  добавим catalog аккуратно
s = re.sub(
    r'render_html_report\(\s*code\s*,\s*vectors\s*\)',
    r'render_html_report(code, vectors, getattr(st,"answers",{}) or {}, catalog, {"raw":{}, "pairs":[]})',
    s
)

p.write_text(s, encoding="utf-8")
print("OK: main.py  render_html_report теперь получает catalog.")