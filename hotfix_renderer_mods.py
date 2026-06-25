# hotfix_renderer_mods.py — отчёт с модификаторами
from pathlib import Path
Path("src/result_renderer.py").write_text(r"""
from typing import List, Tuple, Dict
from .question_loader import load_catalog

def _by_family(code: str) -> str:
    return (code or "G")[0].upper()

def _choose_catalog(code: str):
    fam=_by_family(code)
    cat=load_catalog() or []
    for it in cat:
        if it.get("code")==code: return it
    for it in cat:
        if it.get("code_family")==fam: return it
    return {}

def _neighbors_fmt(neighbors):
    if not neighbors: return []
    out=[]
    for n in neighbors:
        if isinstance(n,(list,tuple)) and len(n)>=1: out.append(str(n[0]))
        else: out.append(str(n))
    return out

def _esc(s:str)->str:
    s="" if s is None else str(s)
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def _li(items: List[str]) -> str:
    if not items: return "<ul><li>—</li></ul>"
    return "<ul>"+"".join(f"<li>{_esc(i)}</li>" for i in items)+"</ul>"

def _tags(items: List[str]) -> str:
    if not items: return ""
    return "".join(f"<span class=\\"tag\\">{_esc(i)}</span>" for i in items)

AXES = {
    "E": ("Исследователь","Осваиватель"),
    "C": ("Корсар","Пират"),
    "B": ("Бульдог","Папильон"),
    "O": ("Осваиватель","Исследователь"),  # симметричные ключи на всякий
    "P": ("Пират","Корсар"),
    "Pap": ("Папильон","Бульдог"),
}

def _mods_table(mods: Dict[str,float]) -> str:
    if not mods: 
        return "<p class='muted'>Пока нет достаточных данных — ответов по модификаторам было мало.</p>"
    # нормализуем по осям: E/O, C/P, B/Pap
    pairs=[("E","O"),("C","P"),("B","Pap")]
    rows=[]
    for left,right in pairs:
        l,r=AXES[left][0],AXES[left][1]
        val = float(mods.get(left,0))-float(mods.get(right,0))
        tilt = l if val>0 else right
        badge = f"{tilt} ({'+' if val>=0 else ''}{val:.1f})"
        rows.append(f"<tr><td>{_esc(l)} ↔ {_esc(r)}</td><td>{badge}</td></tr>")
    head="<thead><tr><th>Ось</th><th>Смещение</th></tr></thead>"
    body="<tbody>"+ "".join(rows) +"</tbody>"
    return f"<table>{head}{body}</table>"

def render_short_card(code: str) -> str:
    fam=_by_family(code)
    names={"G":"Голова","K":"Концепт","T":"Техника","S":"Связи"}
    return f"🔎 Твой индотип: *{code}* — {names.get(fam,'Профиль')}"

def render_html_report(code: str, vectors: dict, features: dict, neighbors, mods=None):
    item=_choose_catalog(code)
    fam=_by_family(code)
    title=item.get("title", f"{fam} — профиль")
    one_liner=item.get("one_liner","Твой ведущий способ действовать и принимать решения.")
    description=item.get("description","Развёрнутое описание профиля: как ты смотришь на задачи, какие предпочитаешь способы и где раскрываешься лучше всего.")
    strengths=item.get("strengths",["Стратегичность","Сбор картины целиком"])
    pitfalls=item.get("pitfalls",["Перебор контроля","Риск затянуть обсуждение"])
    grow=item.get("grow",["Гибкость","Малые быстрые пробы"])
    activities=item.get("activities",["Организация процессов","Прототипирование","Поддержка команды"])
    subjects=item.get("subjects",["Математика","Литература"])
    jobs=item.get("jobs",["Куратор проектов","Редактор","Инженер-практик","Координатор"])

    vecs=sorted(vectors.items(), key=lambda x:(-x[1],x[0]))
    rows="".join(f"<tr><td>{_esc(k)}</td><td>{v:.1f}</td></tr>" for k,v in vecs)
    neigh=_neighbors_fmt(neighbors)
    mods_html=_mods_table(mods or {})

    css="""
    <style>
      :root{ --ink:#1b1f23; --muted:#667085; --bg:#f6f7f9; --card:#ffffff;}
      html,body{margin:0;padding:0;color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,Arial;}
      body{
        background:
          linear-gradient(90deg, rgba(0,0,0,.03) 1px, transparent 1px) 0 0/24px 24px,
          linear-gradient(0deg,  rgba(0,0,0,.03) 1px, transparent 1px) 0 0/24px 24px,
          var(--bg);
        padding:32px;
      }
      .wrap{max-width:920px;margin:0 auto;}
      h1{font-size:34px;margin:0 0 16px;}
      h2{font-size:22px;margin:32px 0 12px;}
      p.lead{color:#667085;font-size:18px;margin:0 0 24px;}
      .card{background:var(--card);border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.05);margin:16px 0;}
      table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
      th,td{padding:10px 12px;border-bottom:1px solid #e6e8eb;text-align:left}
      th{color:#475569;font-weight:600}
      .tag{display:inline-block;background:#eef2ff;color:#312e81;padding:4px 10px;border-radius:999px;margin:2px 6px 2px 0;font-size:12px}
      ul{padding-left:18px}
      .grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
      .muted{color:#667085}
    </style>
    """
    html=f"""<!doctype html><html lang='ru'><head><meta charset='utf-8'>
    <title>{_esc(code)} — Профиль</title><meta name='viewport' content='width=device-width, initial-scale=1'>
    {css}</head><body><div class='wrap'>
      <h1>Профиль {_esc(code)}</h1>
      <p class='lead'>{_esc(one_liner)}</p>

      <div class='card'>
        <h2>Баланс векторов</h2>
        <table><thead><tr><th>Вектор</th><th>Баланс</th></tr></thead><tbody>{rows}</tbody></table>
      </div>

      <div class='card'><h2>Коротко о типе</h2><p>{_esc(description)}</p></div>

      <div class='card'><h2>Модификаторы</h2>{mods_html}</div>

      <div class='grid'>
        <div class='card'><h2>Сильные стороны</h2>{_li(strengths)}</div>
        <div class='card'><h2>Возможные ловушки</h2>{_li(pitfalls)}</div>
      </div>

      <div class='grid'>
        <div class='card'><h2>Полезно развивать</h2>{_li(grow)}</div>
        <div class='card'><h2>Подходят активности</h2>{_li(activities)}</div>
      </div>

      <div class='grid'>
        <div class='card'><h2>Учебные предметы</h2>{_tags(subjects)}</div>
        <div class='card'><h2>Профессии и роли</h2>{_tags(jobs)}</div>
      </div>

      <div class='card'><h2>Близкие профили</h2><p class='muted'>{_tags(neigh)}</p></div>
    </div></body></html>"""
    return html
""", encoding="utf-8")
print("OK: отчёт выводит модификаторы и развёрнутый блок описания.")
