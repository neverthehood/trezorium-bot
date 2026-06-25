# hotfix_mods_explanations.py — добавляет краткие пояснения по модификаторам в отчёт
import pathlib, re

p = pathlib.Path("src/result_renderer.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\r","").replace("\t","    ")

# 1) Вставим/обновим словарь описаний
if "MODS_INFO =" not in s:
    s = s.replace(
        "\n# ------\n",
        r'''
# Краткие пояснения по модификаторам (ось = "<left>_<right>")
MODS_INFO = {
    "rational_emotional": {
        "title": "Вектор: разум ↔ чувство",
        "left":  "Рационал",   "right": "Эмоционал",
        "desc_left":  "Опираешься на логику, факты и план.",
        "desc_right": "Чувствуешь людей и контекст, важны эмоции и отношения.",
    },
    "explorer_settler": {
        "title": "Вектор: исследование ↔ освоение",
        "left":  "Исследователь", "right": "Осваиватель",
        "desc_left":  "Тянешься к новому, пробам и гипотезам.",
        "desc_right": "Закрепляешь и доводишь до устойчивости, строишь процессы.",
    },
    "creative_action": {
        "title": "Вектор: креатив ↔ действие",
        "left":  "Креативист", "right": "Акционист",
        "desc_left":  "Генерируешь идеи, образы, формулировки.",
        "desc_right": "Запускаешь дела, доводишь до результата.",
    },
    "corsair_pirate": {
        "title": "Вектор: корсар ↔ пират",
        "left":  "Корсар", "right": "Пират",
        "desc_left":  "Инициативность ради миссии/команды, игра по договорённостям.",
        "desc_right": "Игра ради выгоды/добычи, автономность и риск.",
    },
    "bulldog_papillon": {
        "title": "Вектор: бульдог ↔ папильон",
        "left":  "Бульдог", "right": "Папильон",
        "desc_left":  "Упорство, устойчивость, держишь курс.",
        "desc_right": "Лёгкость, шарм, гибкость и переключаемость.",
    },
    "fire_water": {
        "title": "Вектор: огонь ↔ вода",
        "left":  "Огонь", "right": "Вода",
        "desc_left":  "Скорость, импульс, напор.",
        "desc_right": "Мягкость, адаптивность, терпение.",
    },
    "partisan_discipline": {
        "title": "Вектор: хаос ↔ порядок",
        "left":  "Партизан", "right": "Дисциплинарий",
        "desc_left":  "Обходные пути, гибкая импровизация.",
        "desc_right": "Порядок, регламент, аккуратность.",
    },
    "mahayana_hinayana": {
        "title": "Вектор: вовне ↔ внутрь",
        "left":  "Махаяна", "right": "Хинаяна",
        "desc_left":  "Ориентация на пользу вовне, сеть и среду.",
        "desc_right": "Фокус внутрь: личная эффективность и глубина.",
    },
    "magnetic_inert": {
        "title": "Вектор: тяготение ↔ автономность",
        "left":  "Магнитный", "right": "Немагнитный",
        "desc_left":  "Притягиваешь людей, легко влияешь и соединяешь.",
        "desc_right": "Предпочитаешь автономность и дистанцию.",
    },
    "ambition_statusquo": {
        "title": "Вектор: стремление ↔ довольство",
        "left":  "Честолюбивый", "right": "Статус-кво",
        "desc_left":  "Тянешься выше: рост, новые задачи.",
        "desc_right": "Комфорт в стабильности и текущем положении.",
    },
}
# ------
''', 1)

# 2) Функция рендера таблицы модификаторов с пояснениями
if "def _render_mods_explained(" not in s:
    s += r'''
def _render_mods_explained(mods: dict) -> str:
    pairs = (mods or {}).get("pairs") or []
    if not pairs:
        return (
            "<section class='card'>"
            "<h2>Модификаторы</h2>"
            "<p class='muted'>Пока недостаточно данных для модификаторов.</p>"
            "</section>"
        )
    rows = []
    for p in pairs:
        code = p.get("code","")
        info = MODS_INFO.get(code, {})
        left_name  = info.get("left",  p.get("left","Лево"))
        right_name = info.get("right", p.get("right","Право"))
        title = info.get("title", p.get("title","Ось"))
        score = float(p.get("score", 0.0))
        # Куда смещено
        if abs(score) < 1e-9:
            side_name, desc = "Баланс", "Баланс между полюсами: оба подхода доступны ситуативно."
        elif score > 0:
            side_name, desc = left_name,  info.get("desc_left",  "")
        else:
            side_name, desc = right_name, info.get("desc_right", "")
        rows.append(
            "<tr>"
            f"<td>{title}</td>"
            f"<td><b>{side_name}</b> ({score:+.1f})</td>"
            f"<td class='muted'>{desc}</td>"
            "</tr>"
        )
    return (
        "<section class='card'>"
        "<h2>Модификаторы</h2>"
        "<table class='tbl'>"
        "<thead><tr><th>Ось</th><th>Смещение</th><th>Пояснение</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</section>"
    )
'''

# 3) Вставим вызов этой функции в render_html_report
pat_fun = re.compile(r'(?ms)def\s+render_html_report\s*\([^)]*\)\s*->\s*str:\s*(.*?)\n(?=def\s+|$)')
m = pat_fun.search(s)
if m and "_render_mods_explained(" not in m.group(1):
    body = m.group(1)
    # Попробуем заменить существующий блок «Модификаторы» на наш, либо добавить в конец
    body2 = re.sub(r'(?s)<h2>Модификаторы</h2>.*?</section>', r"{{MODS_BLOCK}}", body)
    body2 = body2.replace(
        "return html",
        "mods_html = _render_mods_explained(mods)\n        html = html.replace('{{MODS_BLOCK}}', mods_html) if '{{MODS_BLOCK}}' in html else (html + mods_html)\n        return html"
    )
    s = s[:m.start(1)] + body2 + s[m.end(1):]

p.write_text(s, encoding="utf-8")
print("OK: пояснения модификаторов добавлены и подключены в отчёте.")
