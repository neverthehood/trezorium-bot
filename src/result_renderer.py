# src/result_renderer.py
# Формирование отчёта (короткий и HTML)

from typing import Any, Dict, List, Optional

from src.mods import compute_mods
from src.indotype_resolver import resolve_indotype


def render_report(
    answers: Dict[str, Any],
    vectors: Dict[str, float],
    catalog: Any
) -> Dict[str, Any]:
    """
    Формирует данные для отчёта.
    
    1. Вычисляет модификаторы (mod_*) из ответов
    2. Определяет индотип по модификаторам
    3. Разделяет векторы (G, S, T, K) и модификаторы
    4. Собирает всё в единую структуру
    """
        # Вычисляем модификаторы из ответов + переданных векторов
    mods_result = compute_mods(answers or {}, catalog, vectors)
    raw_mods = mods_result.get("raw", {})
    
    # Определяем индотип по модификаторам
    indotype = resolve_indotype(mods_result)
    
    # Разделяем чистые векторы (G, S, T, K) и модификаторы
    pure_vectors = {}
    extra_mods = {}
    if vectors:
        for k, v in vectors.items():
            if k in ("G", "S", "T", "K"):
                pure_vectors[k] = v
            elif k.startswith("mod_"):
                extra_mods[k] = v
    
    # Объединяем модификаторы из обоих источников
    merged_mods = dict(raw_mods)
    for k, v in extra_mods.items():
        merged_mods[k] = merged_mods.get(k, 0.0) + v
    
    return {
        "indotype": indotype,
        "vectors": pure_vectors,
        "answers": answers or {},
        "raw_mods": merged_mods,
        "all_vectors": vectors or {}
    }


def render_html_report(
    code: Dict[str, str],
    vectors: Dict[str, float],
    answers: Dict[str, Any],
    catalog: List[Dict[str, Any]],
    mods_result: Dict[str, Any] = None
) -> str:
    """
    Формирует HTML-отчёт на основе кода, векторов, ответов и модификаторов.
    
    Использует шаблон из templates/report.html если доступен.
    """
    mods = prepare_mods_list(mods_result or {})
    
    # Категоризируем модификаторы
    mods_by_group = {
        "thinking": [],    # теоретик/практик
        "social": [],      # экстраверт/интроверт
        "planning": [],    # плановый/спонтанный
        "other": []        # остальные
    }
    
    mod_labels = {
        "theoretical": "Теоретик",
        "natural": "Естественник",
        "practical": "Практик",
        "humanitarian": "Гуманитарий",
        "extro": "Экстраверт",
        "intro": "Интроверт",
        "positive": "Позитив",
        "negative": "Негатив",
        "generator": "Генератор",
        "emitter": "Эмиттер",
        "planned": "Планомерность",
        "spontaneous": "Спонтанность",
        "macro": "Макро",
        "micro": "Микро",
        "head": "Голова",
        "heart": "Сердце",
        "body": "Тело",
        "creativity": "Креативность",
        "athlete": "Атлет",
        "master": "Мастер",
        "risk": "Риск",
        "static": "Статика",
        "scenic": "Сценичность",
        "situational": "Ситуативность",
        "inventor": "Инвентор",
        "aesthetic": "Эстетик"
    }
    
    mod_descriptions = {
        "theoretical": "Склонность к абстрактному мышлению, теории, общим принципам",
        "natural": "Склонность к конкретике, практике, естественному познанию через опыт",
        "extro": "Энергия из общения с людьми, склонность к активному взаимодействию",
        "intro": "Энергия из уединения, склонность к глубокому самоанализу",
        "planned": "Предпочтение структуры, планов, предсказуемости",
        "spontaneous": "Предпочтение гибкости, импровизации, спонтанности",
        "head": "Доминанта интеллектуальной сферы — анализа, логики, познания",
        "heart": "Доминанта эмоциональной сферы — эмпатии, чувств, отношений",
        "body": "Доминанта физической сферы — действий, практики, ручного труда",
        "creativity": "Доминанта творческой сферы — воображения, идей, новизны",
        "positive": "Склонность к позитивному восприятию и доброжелательности",
        "negative": "Склонность к критическому восприятию и настороженности",
        "generator": "Склонность генерировать идеи и решения",
        "emitter": "Склонность излучать и влиять на других",
        "macro": "Склонность видеть общую картину, мыслить масштабно",
        "micro": "Склонность к деталям, точности, нюансам",
        "athlete": "Склонность к физической активности, спорту",
        "master": "Склонность к мастерству, ручному труду",
        "risk": "Склонность к риску и экстремальным ситуациям",
        "static": "Склонность к стабильности и аккуратности",
        "scenic": "Склонность к публичности и выступлениям",
        "situational": "Склонность к импровизации и действиям по обстоятельствам",
        "inventor": "Склонность к изобретательству и новаторству",
        "aesthetic": "Склонность к эстетике и художественному творчеству",
        "humanitarian": "Склонность к гуманитарному, человеко-центрированному подходу"
    }
    
    for m in mods:
        m["explanation"] = mod_descriptions.get(m["name"], "")
        # Группируем
        if m["name"] in ("theoretical", "natural", "head", "practical"):
            mods_by_group["thinking"].append(m)
        elif m["name"] in ("extro", "intro", "positive", "negative", "generator", "emitter", "heart"):
            mods_by_group["social"].append(m)
        elif m["name"] in ("planned", "spontaneous", "macro", "micro", "static"):
            mods_by_group["planning"].append(m)
        else:
            mods_by_group["other"].append(m)
    
    # Строим HTML
    
    # Блок векторов со шкалами
    vectors_rows = ""
    vector_info = {
        "G": "Голова — анализ и логика",
        "S": "Сердце — эмпатия и связи",
        "T": "Руки — практика и действие",
        "K": "Креатив — воображение и идеи"
    }
    
    if vectors:
        max_val = max(vectors.values()) if vectors else 1
        if max_val <= 0:
            max_val = 1
        
        for v_code in ("G", "S", "T", "K"):
            val = vectors.get(v_code, 0.0)
            pct = min(100, int((val / max_val) * 100)) if max_val > 0 else 0
            label = vector_info.get(v_code, v_code)
            vectors_rows += f"""
            <div class="vector-row">
                <div class="vector-label"><strong>{v_code}</strong><span class="vector-desc">{label}</span></div>
                <div class="vector-bar-bg">
                    <div class="vector-bar" style="width:{pct}%"></div>
                </div>
                <div class="vector-value">{val:.1f}</div>
            </div>"""
    
    # Модификаторы
    mods_html = ""
    for group_name, group_mods in mods_by_group.items():
        if not group_mods:
            continue
        group_labels = {
            "thinking": "Стиль мышления",
            "social": "Социальный стиль",
            "planning": "Стиль планирования",
            "other": "Дополнительные черты"
        }
        items = "".join(
            f"""<div class="mod-item">
                <div class="mod-header">
                    <span class="mod-name">{mod_labels.get(m['name'], m['name'].capitalize())}</span>
                    <span class="mod-score">{'+' if m['score'] > 0 else ''}{m['score']:.1f}</span>
                </div>
                <div class="mod-bar-bg">
                    <div class="mod-bar {('mod-bar-pos' if m['score'] > 0 else 'mod-bar-neg')}" 
                         style="width:{min(100, abs(m['score']) * 20)}%"></div>
                </div>
                <div class="mod-expl">{m['explanation']}</div>
            </div>"""
            for m in group_mods
        )
        mods_html += f"""
        <div class="mod-group">
            <h3>{group_labels.get(group_name, group_name)}</h3>
            {items}
        </div>"""
    
    if not mods_html:
        mods_html = "<p class='muted'>Дополнительные модификаторы не выражены.</p>"
    
    # Описание профиля из каталога
    code_str = code.get("code", "—")
    code_title = code.get("title", "")
    code_desc = code.get("description", "")
    
    # Ищем описание в каталоге по code_family
    family_desc = ""
    strengths = []
    pitfalls = []
    grow_list = []
    activities = []
    subjects = []
    jobs = []
    
    if catalog and isinstance(catalog, list):
        for entry in catalog:
            entry_code = entry.get("code_family", "")
            if entry_code and code_str and entry_code in code_str:
                family_desc = entry.get("description", "")
                strengths = entry.get("strengths", [])
                pitfalls = entry.get("pitfalls", [])
                grow_list = entry.get("grow", [])
                activities = entry.get("activities", [])
                subjects = entry.get("subjects", [])
                jobs = entry.get("jobs", [])
                break
    
    # Формируем блоки
    strengths_html = "".join(f"<li>{s}</li>" for s in strengths) if strengths else "<li>—</li>"
    pitfalls_html = "".join(f"<li>{p}</li>" for p in pitfalls) if pitfalls else "<li>—</li>"
    grow_html = "".join(f"<li>{g}</li>" for g in grow_list) if grow_list else "<li>—</li>"
    activities_html = "".join(f"<li>{a}</li>" for a in activities) if activities else "<li>—</li>"
    subjects_tags = "".join(f'<span class="tag">{s}</span>' for s in subjects) if subjects else ""
    jobs_tags = "".join(f'<span class="tag">{j}</span>' for j in jobs) if jobs else ""
    
    html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{code_str} — Trezorium</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{ --ink: #1b1f23; --muted: #667085; --bg: #f0f2f5; --card: #ffffff; --accent: #3b82f6; --accent2: #8b5cf6; --green: #10b981; --red: #ef4444; --amber: #f59e0b; }}
  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; color: var(--ink); font: 16px/1.6 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }}
  body {{ background: var(--bg); padding: 0; }}
  .wrap {{ max-width: 920px; margin: 0 auto; padding: 24px 16px; }}
  
  /* Header */
  .header {{ background: linear-gradient(135deg, var(--accent), var(--accent2)); color: white; border-radius: 20px; padding: 32px; margin-bottom: 24px; }}
  .header h1 {{ font-size: 36px; margin: 0 0 4px; font-weight: 700; letter-spacing: -0.5px; }}
  .header .code-badge {{ display: inline-block; background: rgba(255,255,255,0.2); padding: 4px 14px; border-radius: 999px; font-size: 14px; margin-top: 8px; }}
  .header .subtitle {{ font-size: 20px; opacity: 0.95; margin: 8px 0 0; }}
  
  /* Cards */
  .card {{ background: var(--card); border-radius: 16px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 20px; }}
  .card h2 {{ font-size: 20px; margin: 0 0 16px; color: var(--muted); font-weight: 600; letter-spacing: -0.3px; }}
  .card h3 {{ font-size: 16px; margin: 16px 0 8px; color: var(--ink); font-weight: 600; }}
  
  /* Vectors */
  .vector-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
  .vector-label {{ min-width: 180px; }}
  .vector-label strong {{ font-size: 18px; margin-right: 8px; }}
  .vector-desc {{ color: var(--muted); font-size: 13px; }}
  .vector-bar-bg {{ flex: 1; height: 12px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }}
  .vector-bar {{ height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 999px; transition: width 0.5s; }}
  .vector-value {{ min-width: 40px; font-weight: 600; font-variant-numeric: tabular-nums; }}
  
  /* Description */
  .desc-text {{ font-size: 16px; line-height: 1.7; color: #374151; }}
  
  /* Grid */
  .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
  .grid-3 {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
  .grid ul {{ padding-left: 18px; margin: 0; }}
  .grid li {{ margin-bottom: 6px; line-height: 1.5; }}
  .tag {{ display: inline-block; background: #eef2ff; color: #312e81; padding: 4px 12px; border-radius: 999px; margin: 3px 4px 3px 0; font-size: 13px; white-space: nowrap; }}
  .muted {{ color: var(--muted); }}
  
  /* Modifiers */
  .mod-group {{ margin-bottom: 20px; }}
  .mod-group h3 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); margin-bottom: 12px; }}
  .mod-item {{ margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid #f0f0f0; }}
  .mod-item:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
  .mod-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
  .mod-name {{ font-weight: 600; font-size: 15px; }}
  .mod-score {{ font-size: 14px; padding: 2px 10px; border-radius: 999px; background: #f3f4f6; font-weight: 600; }}
  .mod-bar-bg {{ height: 6px; background: #e5e7eb; border-radius: 999px; overflow: hidden; margin-bottom: 4px; }}
  .mod-bar {{ height: 100%; border-radius: 999px; transition: width 0.5s; }}
  .mod-bar-pos {{ background: var(--green); }}
  .mod-bar-neg {{ background: var(--amber); }}
  .mod-expl {{ font-size: 13px; color: var(--muted); }}
  
  /* Footer */
  .footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 16px; }}
</style>
</head>
<body>
<div class="wrap">
  
  <div class="header">
    <h1>{code_str}</h1>
    <div class="subtitle">{code_title}</div>
    <div class="code-badge">Trezorium · Психологический профиль</div>
  </div>

  <div class="card">
    <h2>Баланс векторов</h2>
    {vectors_rows}
  </div>

  <div class="card">
    <h2>Описание типа</h2>
    <p class="desc-text">{code_desc}</p>
    {f'<p class="desc-text" style="margin-top:12px">{family_desc}</p>' if family_desc and family_desc != code_desc else ''}
  </div>

  <div class="grid">
    <div class="card">
      <h2>Сильные стороны</h2>
      <ul>{strengths_html}</ul>
    </div>
    <div class="card">
      <h2>Возможные ловушки</h2>
      <ul>{pitfalls_html}</ul>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Полезно развивать</h2>
      <ul>{grow_html}</ul>
    </div>
    <div class="card">
      <h2>Подходящие активности</h2>
      <ul>{activities_html}</ul>
    </div>
  </div>

  {f'''
  <div class="grid-3">
    <div class="card">
      <h2>Учебные предметы</h2>
      {subjects_tags or '<span class="muted">—</span>'}
    </div>
    <div class="card">
      <h2>Профессии и роли</h2>
      {jobs_tags or '<span class="muted">—</span>'}
    </div>
  </div>
  ''' if subjects_tags or jobs_tags else ''}

  <div class="card">
    <h2>Модификаторы личности</h2>
    {mods_html}
  </div>

  <div class="footer">
    Trezorium · Отчёт сгенерирован автоматически · {len(answers)} ответов
  </div>
  
</div>
</body>
</html>"""
    return html


def render_short_card(code: str, vectors: Dict[str, float]) -> str:
    """Формирует короткое текстовое представление результата (в Markdown)."""
    if not code:
        code = "—"
    vs = " / ".join(f"{k}: {round(vectors.get(k, 0.0), 2)}" for k in ("G", "S", "T", "K"))
    return f"*Ваш код*: `{code}`\n\n*Баланс векторов:* {vs}"


def prepare_mods_list(mods_result: Dict[str, Any]) -> list:
    raw = mods_result.get("raw", {})
    mods = []
    for key, value in raw.items():
        if not key.startswith("mod_"):
            continue
        mod_name = key.replace("mod_", "")
        mods.append({
            "name": mod_name,
            "score": round(value, 2)
        })
    mods.sort(key=lambda m: abs(m["score"]), reverse=True)
    return mods