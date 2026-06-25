# hard_fix_answers_and_vectors.py
# - полностью переписывает handler ans()
# - добавляет надёжный пересчёт векторов из st.answers
# - finish_and_report() строит html из пересчитанных vectors и mods

import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\r","").replace("\t","    ")

# ---------- 1) helper-функции (вставим один раз) ----------
if "def _recompute_vectors_from_answers(" not in s:
    helper = r'''
def _get(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

def _iter_opts(q):
    opts = _get(q, "options") or []
    try: return list(opts)
    except TypeError: return opts

def _weights_dict(opt):
    w = _get(opt, "weights", {}) or {}
    return dict(w) if isinstance(w, dict) else {}

def _find_q_in_bank(qid: str):
    try:
        for q in bank.questions:
            if _get(q, "id") == qid:
                return q
    except Exception:
        pass
    return None

def _recompute_vectors_from_answers(answers):
    totals = {"G":0.0,"S":0.0,"T":0.0,"K":0.0}
    for qid, ans in (answers or {}).items():
        if not isinstance(ans, dict): 
            continue
        chosen = []
        for k in ("best","single","answer","opt"):
            v = ans.get(k)
            if v: chosen.append(v)
        worst = ans.get("worst")
        q = _find_q_in_bank(qid)
        if not q:
            continue
        # плюсовой вклад
        for oid in chosen:
            for o in _iter_opts(q):
                if _get(o, "id") == oid:
                    for k, v in _weights_dict(o).items():
                        if k in totals:
                            totals[k] += float(v)
        # отрицательный вклад (worst)
        if worst:
            for o in _iter_opts(q):
                if _get(o, "id") == worst:
                    for k, v in _weights_dict(o).items():
                        if k in totals:
                            totals[k] -= float(v)
    return totals
'''
    # вставим перед finish_and_report
    s = re.sub(r'(?m)^\s*async\s+def\s+finish_and_report\b',
               helper + "\nasync def finish_and_report", s, count=1)

# ---------- 2) переписываем handler ans() целиком ----------
pat_ans = re.compile(
    r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("ans:"\)\)\s*\n'
    r'\s*async\s+def\s+ans\s*\([^)]*\):\s*'
    r'(.*?)'
    r'(?=^\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z)', re.M)

def new_ans():
    return r'''
@router.callback_query(F.data.startswith("ans:"))
async def ans(cb: CallbackQuery):
    _, qid, opt_id = cb.data.split(":", 2)
    st = st_for(cb.message.chat.id)
    q = find_q(qid)
    if not q:
        await safe_answer(cb, "Ок")
        return
    # сохранить ответ
    st.answers.setdefault(qid, {})
    st.answers[qid]["single"] = opt_id
    st.answers[qid]["answer"] = opt_id
    asked = st.answers[qid].get("_asked_ts")
    if asked:
        st.answers[qid]["single_ms"] = int((time.time() - asked) * 1000)
    # применить веса (если есть)
    opt = next((o for o in q.options if getattr(o, "id", None) == opt_id), None)
    if opt:
        apply_weights(st, getattr(opt, "weights", {}) or {}, 1.0)
        label = opt_label(opt, st.mode)
    else:
        label = "Выбрано"
    await safe_answer(cb, f"Выбрано: {label}")
    await after(cb.message, st)
'''.lstrip("\n")

if pat_ans.search(s):
    s = pat_ans.sub(new_ans(), s, count=1)
else:
    # если не нашли — добавим в конец файла
    s = s.rstrip() + "\n\n" + new_ans()

# ---------- 3) finish_and_report — считаем vectors/mods сами ----------
pat_fin = re.compile(
    r'(?ms)^async\s+def\s+finish_and_report\s*\([^)]*\):\s*'
    r'(.*?)'
    r'(?=^\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z)', re.M)

def new_finish():
    return r'''
async def finish_and_report(m, st):
    """Финиш: рассчитываем векторы/модификаторы и отправляем один HTML."""
    # Векторы прямо из ответов
    try:
        vectors = _recompute_vectors_from_answers(getattr(st, "answers", {}) or {})
    except Exception:
        vectors = {"G":0.0,"S":0.0,"T":0.0,"K":0.0}

    # Код профиля
    try:
        code = pick_result(vectors)
    except Exception:
        code = "—"

    # Короткая карточка — только если код валиден
    try:
        short = render_short_card(code, vectors)
        if code and code != "—":
            await m.answer(short)
    except Exception:
        pass

    # Модификаторы
    try:
        mods = compute_mods(getattr(st, "answers", {}) or {}, bank) or {"raw": {}, "pairs": []}
    except Exception:
        mods = {"raw": {}, "pairs": []}

    # HTML отчёт
    try:
        html = render_html_report(code, vectors, getattr(st, "answers", {}) or {}, [], mods)
    except TypeError:
        try:
            html = render_html_report(code, vectors, getattr(st, "answers", {}) or {}, [])
        except Exception:
            html = "<h1>Отчёт</h1>"

    # Отправка одним файлом
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
'''.lstrip("\n")

if pat_fin.search(s):
    s = pat_fin.sub(new_finish(), s, count=1)
else:
    s = s.rstrip() + "\n\n" + new_finish()

p.write_text(s, encoding="utf-8")
print("OK: ans() переписан, векторы пересчитываются, отчёт шлётся с данными.")
