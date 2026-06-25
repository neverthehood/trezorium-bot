# hotfix_result_renderer.py — отчёт с нормальными разделами
from pathlib import Path
p = Path("src/result_renderer.py")
p.write_text("""from jinja2 import Template
from .question_loader import load_catalog, load_report_template

def _by_family(code: str):
    # семья — первая буква кода, если нет — по топовому вектору
    return (code or 'G')[0].upper()

def _choose_catalog(code: str):
    fam = _by_family(code)
    cat = load_catalog() or []
    # точное совпадение по коду
    for it in cat:
        if it.get('code') == code:
            return it
    # семейство
    for it in cat:
        if it.get('code_family') == fam:
            return it
    return None

def _neighbors_fmt(neighbors):
    if not neighbors: return []
    out=[]
    for n in neighbors:
        if isinstance(n,(list,tuple)) and len(n)>=1:
            out.append(str(n[0]))
        else:
            out.append(str(n))
    return out

def render_short_card(code: str) -> str:
    fam = _by_family(code)
    names = {'G':'Голова','K':'Концепт','T':'Техника','S':'Связи'}
    return f"🔎 Твой индотип: *{code}* — {names.get(fam,'Профиль')}"

def render_html_report(code: str, vectors: dict, features: dict, neighbors):
    tpl = Template(load_report_template("report.html"))
    item = _choose_catalog(code) or {}
    fam = _by_family(code)

    # значения по умолчанию из семейства
    title = item.get("title", f"{fam} — профиль")
    one_liner = item.get("one_liner", "Короткое описание профиля.")
    description = item.get("description", "Этот профиль описывает твой ведущий способ действовать и принимать решения.")
    strengths = item.get("strengths", ["Сильная сторона №1","Сильная сторона №2"])
    pitfalls = item.get("pitfalls", ["Возможная ловушка №1","Возможная ловушка №2"])
    grow = item.get("grow", ["Навык для роста №1","Навык для роста №2"])
    activities = item.get("activities", ["Активность №1","Активность №2"])
    subjects = item.get("subjects", ["Математика","Литература"])
    jobs = item.get("jobs", ["Роль/профессия"])

    vecs = sorted(vectors.items(), key=lambda x: (-x[1], x[0]))
    html = tpl.render(
        code=code, title=title, one_liner=one_liner, description=description,
        strengths=strengths, pitfalls=pitfalls, grow=grow,
        activities=activities, subjects=subjects, jobs=jobs,
        vectors=vecs, neighbors=_neighbors_fmt(neighbors)
    )
    return html
""", encoding="utf-8")
print("OK: src/result_renderer.py — обновлён.")
