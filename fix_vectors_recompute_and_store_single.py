# fix_vectors_recompute_and_store_single.py
# - сохраняем single/answer в ans()
# - пересчитываем векторы из st.answers, если vector_totals() пустой

import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\t","    ").replace("\r","")

# 1) Патч handler ans: — сохранить выбор
pat_ans = re.compile(
    r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("ans:"\)\)\s*\n'
    r'\s*async\s+def\s+ans\s*\([^)]*\):\s*(.*?)'
    r'(?=^\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z)', re.M)

m = pat_ans.search(s)
if not m:
    raise SystemExit("Не нашёл handler ans:")
ans_body = m.group(1)
if 'st.answers.setdefault(qid, {})' not in ans_body or '["single"]' not in ans_body:
    ans_body = re.sub(
        r'(opt\s*=\s*next\([^)]*\)\s*)\n',
        r'\1\n        st.answers.setdefault(qid, {})\n'
        r'        st.answers[qid]["single"] = opt_id\n'
        r'        st.answers[qid]["answer"] = opt_id\n',
        ans_body, count=1)
    s = s[:m.start(1)] + ans_body + s[m.end(1):]

# 2) Вставим помощник пересчёта векторов (если его ещё нет)
if "def _recompute_vectors_from_answers(" not in s:
    helper = r'''
def _get(obj, key, default=None):
    return getattr(obj, key, default) if not isinstance(obj, dict) else obj.get(key, default)

def _iter_opts(q):
    opts = _get(q, "options") or []
    try: return list(opts)
    except TypeError: return opts

def _find_q_any(catalog, qid):
    if hasattr(catalog, "by_id"):
        by = getattr(catalog, "by_id")
        if isinstance(by, dict) and qid in by: return by[qid]
    try:
        for q in catalog.questions:
            if _get(q, "id") == qid: return q
    except Exception:
        pass
    return None

def _weights_dict(opt):
    w = _get(opt, "weights", {}) or {}
    return dict(w) if isinstance(w, dict) else {}

def _recompute_vectors_from_answers(answers, catalog):
    totals = {"G":0.0,"S":0.0,"T":0.0,"K":0.0}
    for qid, ans in (answers or {}).items():
        if not isinstance(ans, dict): continue
        chosen = []
        for k in ("best","single","answer","opt"):
            v = ans.get(k)
            if v: chosen.append(v)
        worst = ans.get("worst")
        q = _find_q_any(catalog, qid)
        if not q: 
            continue
        # плюсовые
        for oid in chosen:
            for o in _iter_opts(q):
                if _get(o,"id")==oid:
                    for k,v in _weights_dict(o).items():
                        if k in totals: totals[k] += float(v)
        # минус за worst
        if worst:
            for o in _iter_opts(q):
                if _get(o,"id")==worst:
                    for k,v in _weights_dict(o).items():
                        if k in totals: totals[k] -= float(v)
    return totals
'''
    # вставим помощник перед finish_and_report
    s = re.sub(r'(?m)^\s*async\s+def\s+finish_and_report\b', helper + "\nasync def finish_and_report", s, count=1)

# 3) Перепишем начало finish_and_report: подстраховаться пересчётом
pat_fin = re.compile(
    r'(?ms)^async\s+def\s+finish_and_report\s*\([^)]*\):\s*(.*?)'
    r'(?:\n(?=^\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z))', re.M)
m2 = pat_fin.search(s)
if not m2:
    raise SystemExit("Не нашёл finish_and_report()")
body = m2.group(1)

# заменим участок с vectors/pick_result на устойчивый вариант
body = re.sub(
    r'(?s)^\s*#\s*Короткая карточка.*?pass\n\n',
    (
    '    # Векторы и код профиля\n'
    '    try:\n'
    '        vectors = vector_totals(st)\n'
    '    except Exception:\n'
    '        vectors = {}\n'
    '    # Если вектора пустые/нули — пересчитаем из ответов\n'
    '    try:\n'
    '        if not vectors or (sum(abs(v) for v in vectors.values()) == 0):\n'
    '            try:\n'
    '                catalog = load_catalog(getattr(st, "mode", "teen"), getattr(st, "style", "classic"))\n'
    '            except Exception:\n'
    '                catalog = bank\n'
    '            vectors = _recompute_vectors_from_answers(getattr(st, "answers", {}) or {}, catalog)\n'
    '    except Exception:\n'
    '        pass\n'
    '    try:\n'
    '        code = pick_result(vectors)\n'
    '    except Exception:\n'
    '        code = "—"\n'
    '\n'
    '    # Короткая карточка — только если код валидный\n'
    '    try:\n'
    '        short = render_short_card(code, vectors)\n'
    '        if code and code != "—":\n'
    '            await m.answer(short)\n'
    '    except Exception:\n'
    '        pass\n'
    '\n'
    ),
    body, count=1
)

s = s[:m2.start(1)] + body + s[m2.end(1):]
p.write_text(s, encoding="utf-8")
print("OK: сохранение single и пересчёт векторов добавлены.")
