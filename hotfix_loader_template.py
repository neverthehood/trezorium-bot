# hotfix_loader_template.py — добавляет совместимую load_report_template(name="report.html")
import pathlib

p = pathlib.Path("src/question_loader.py")
src = p.read_text(encoding="utf-8")

patch = """

def load_report_template(name: str = "report.html") -> str:
    \"\"\"HTML-шаблон отчёта из templates/<name>. Если нет — минимальный запасной.\"\"\"
    try:
        BASE = pathlib.Path(__file__).parent.parent
        TEMPLATES_DIR = BASE / "templates"
        path = TEMPLATES_DIR / name
        return path.read_text(encoding="utf-8")
    except Exception:
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>Отчёт</title></head>"
            "<body style='font-family:Segoe UI,Arial,sans-serif;background:#f7f8fa;margin:24px'>"
            "<h1>{{code}} — {{title}}</h1>"
            "<p>{{one_liner}}</p>"
            "<div>{{description}}</div>"
            "<h3>Баланс векторов</h3>{{vectors_table}}"
            "</body></html>"
        )
"""

if "def load_report_template(" not in src or "name:" not in src:
    if not src.endswith("\n"): src += "\n"
    src += patch
    p.write_text(src, encoding="utf-8")
    print("OK: совместимая load_report_template добавлена.")
else:
    print("load_report_template уже совместима — пропускаем.")
