# fix_finish_and_report_rewrite.py — переписывает finish_and_report() и добавляет helper для векторов
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8").replace("\t","    ").replace("\r","")

# --- helper: если нет, добавим ---
helper = r"def compute_vectors_from_answers("
if helper not in s:
    insert_point = s.find("\n\nasync def")  # перед первым async def
    helper_code = '''
def compute_vectors_from_answers(answers, catalog):
    """Подсчёт G/S/T/K напрямую из ответов, на случай если ядро не вернуло векторы."""
    totals = {"G": 0.0, "S": 0.0, "T": 0.0, "K": 0.0}
    # Индекс вопросов
    items = getattr(catalog, "questions", None) or []
    by_id = getattr(catalog, "by_id", None)
    if isinstance(by_id, dict) and not items:
        items = list(by_id.values())
    qidx = {}
    for q in items:
        qid = getattr(q, "id", None) or (q.get("id") if isinstance(q, dict) else None)
        if qid:
            qidx[qid] = q
    # Обход ответов
    for qid, ans in (answers or {}).items():
        if not isinstance(ans, dict):
            continue
        q = qidx.get(qid)
        if not q:
            continue
        opts = getattr(q, "options", None) or (q.get("options") if isinstance(q, dict) else []) or []
        oidx = {}
        for o in opts:
            oid = getattr(o, "id", None) or (o.get("id") if isinstance(o, dict) else None)
            if oid:
                oidx[oid] = o
        chosen = []
        for k in ("best", "opt", "single", "answer"):
            v = ans.get(k)
            if v:
                chosen.append(v)
        worst = ans.get("worst")
        def upd(oid, sign):
            o = oidx.get(oid)
            if not o:
                return
            w = getattr(o, "weights", None) or (o.get("weights") if isinstance(o, dict) else {}) or {}
            for k in ("G","S","T","K"):
                v = w.get(k)
                if v:
                    totals[k] += sign * float(v)
        for oid in chosen:
            upd(oid, +1.0)
        if worst:
            upd(worst, -1.0)
    return totals

'''
    s = s[:insert_point] + helper_code + s[insert_point:]

# --- переписываем finish_and_report полностью ---
pat = re.compile(r"(?ms)^async\s+def\s+finish_and_report\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)")
new_func = '''
async def finish_and_report(m, st):
    """Финиш опроса: считаем результат, готовим HTML и шлём одним файлом."""
    # 1) Векторы
    try:
        vectors = vector_totals(st)
    except Exception:
        vectors = {}
    # fallback: если векторы пустые/нули — считаем из ответов
    try:
        if not any(abs(float(v)) > 1e-9 for v in (vectors or {}).values()):
            catalog = load_catalog(getattr(st, "mode", "teen"), getattr(st, "style", "classic"))
            vectors = compute_vectors_from_answers(getattr(st, "answers", {}) or {}, catalog)
    except Exception:
        pass

    # 2) Код типа + короткая карточка
    try:
        code = pick_result(vectors)
    except Exception:
        code = "—"
    try:
        short = render_short_card(code, vectors)
        if code and code != "—":
            await m.answer(short)
    except Exception:
        pass  # карточка не критична

    # 3) Модификаторы
    mods = {"raw": {}, "pairs": []}
    try:
        catalog = load_catalog(getattr(st, "mode", "teen"), getattr(st, "style", "classic"))
        try:
            mods = compute_mods(getattr(st, "answers", {}) or {}, catalog) or mods
        except Exception:
            pass
    except Exception:
        pass

    # 4) HTML отчёт
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

    # 5) Отправка одним файлом
    try:
        import time, pathlib
        reports_dir = pathlib.Path("data/reports"); reports_dir.mkdir(parents=True, exist_ok=True)
        fname = f"report_{m.chat.id}_{int(time.time())}.html"
        fpath = reports_dir / fname
        fpath.write_text(html, encoding="utf-8")
        await m.answer_document(FSInputFile(fpath, filename=fname), caption="Полная версия отчёта (HTML)")
    except Exception:
        try:
            await m.answer(html[:3500])
        except Exception:
            await m.answer("Готово! (не удалось отправить файл отчёта)")
'''
s = pat.sub(new_func.strip()+"\n", s)

p.write_text(s, encoding="utf-8")
print("OK: finish_and_report переписан; helper добавлен при необходимости.")
