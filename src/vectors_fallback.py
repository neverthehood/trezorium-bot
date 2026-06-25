# -*- coding: utf-8 -*-
# src/vectors_fallback.py — считаем векторы G/S/T/K из ответов

from typing import Any, Dict, Iterable

def _getv(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def _weights(obj: Any) -> Dict[str, float]:
    w = _getv(obj, "weights", {}) or {}
    return dict(w) if isinstance(w, dict) else {}

def _iter_options(q: Any) -> Iterable[Any]:
    opts = _getv(q, "options") or []
    try:
        return list(opts)
    except TypeError:
        return opts

def _find_question(catalog: Any, qid: str):
    if isinstance(catalog, dict) and qid in catalog:
        return catalog[qid]
    by_id = _getv(catalog, "by_id")
    if isinstance(by_id, dict) and qid in by_id:
        return by_id[qid]
    if isinstance(catalog, (list, tuple)):
        for q in catalog:
            if _getv(q, "id") == qid:
                return q
    return None

def _find_option(q: Any, oid: str):
    for o in _iter_options(q):
        if _getv(o, "id") == oid:
            return o
    return None

def compute_vectors_from_answers(answers: Dict[str, Any], catalog: Any) -> Dict[str, float]:
    totals = {"G": 0.0, "S": 0.0, "T": 0.0, "K": 0.0}
    for qid, ans in (answers or {}).items():
        if not isinstance(ans, dict):
            continue

        chosen = []
        for k in ("best", "opt", "single", "answer"):
            v = ans.get(k)
            if v:
                chosen.append(v)
        worst = ans.get("worst")

        q = _find_question(catalog, qid)
        if not q:
            continue

        # плюсовые ответы
        for oid in chosen:
            opt = _find_option(q, oid)
            if not opt:
                continue
            w = _weights(opt)
            for k in ("G", "S", "T", "K"):
                if k in w:
                    totals[k] += float(w[k])

        # «worst» вычитаем
        if worst:
            opt = _find_option(q, worst)
            if opt:
                w = _weights(opt)
                for k in ("G", "S", "T", "K"):
                    if k in w:
                        totals[k] -= float(w[k])

    return totals
