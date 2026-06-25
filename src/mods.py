# src/mods.py — вычисление модификаторов (UTF-8)
# Версия, подготовленная под систему 32 индотипов

from collections import defaultdict
from typing import Any, Dict, Iterable, Optional

# -------- helpers: поддержка dict и pydantic/BaseModel --------
def getv(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def weights_of(obj: Any) -> Dict[str, float]:
    w = getv(obj, "weights", {}) or {}
    return dict(w) if isinstance(w, dict) else {}

def iter_options(q: Any) -> Iterable[Any]:
    opts = getv(q, "options") or []
    try:
        return list(opts)
    except TypeError:
        return opts

def find_question(catalog: Any, qid: str):
    # 1) прямой dict: id->вопрос
    if isinstance(catalog, dict) and qid in catalog:
        return catalog[qid]
    # 2) у каталога есть by_id
    by_id = getv(catalog, "by_id")
    if isinstance(by_id, dict) and qid in by_id:
        return by_id[qid]
    # 3) каталог — список
    if isinstance(catalog, (list, tuple)):
        for q in catalog:
            if getv(q, "id") == qid:
                return q
    return None

def find_option(q: Any, oid: str):
    for o in iter_options(q):
        if getv(o, "id") == oid:
            return o
    return None
# -------- end helpers --------


def compute_mods(
    answers: Dict[str, Any],
    catalog: Any,
    vectors: Optional[Dict[str, float]] = None
):
    """
    Считает модификаторы по ответам и переданным векторам.

    Логика:
    - берём веса всех выбранных опций (best / opt / single / answer)
    - суммируем все ключи вида mod_* и G/S/T/K
    - если есть worst — вычитаем его вклад
    - используем vectors (из session state) как дополнительный источник
    - вычисляем первичные модификаторы (head, heart, body, creativity)

    Возвращаем:
      "raw" — все накопленные модификаторы
    """

    sums = defaultdict(float)
    vec = defaultdict(float)  # G, S, T, K из ответов

    for qid, ans in (answers or {}).items():
        if not isinstance(ans, dict):
            continue

        # Собираем выбранные варианты
        chosen_ids = []
        for k in ("best", "opt", "single", "answer"):
            v = ans.get(k)
            if v:
                chosen_ids.append(v)

        worst_id = ans.get("worst")

        q = find_question(catalog, qid)
        if not q:
            continue

        # Плюсуем вклад выбранных вариантов
        for oid in chosen_ids:
            opt = find_option(q, oid)
            if not opt:
                continue

            for k, v in weights_of(opt).items():
                if k.startswith("mod_"):
                    sums[k] += float(v)
                elif k in ("G", "S", "T", "K"):
                    vec[k] += float(v)

        # Минусуем вклад worst (если вдруг используется ранжирование)
        if worst_id:
            opt = find_option(q, worst_id)
            if opt:
                for k, v in weights_of(opt).items():
                    if k.startswith("mod_"):
                        sums[k] -= float(v)
                    elif k in ("G", "S", "T", "K"):
                        vec[k] -= float(v)

    # Дополняем векторами из session state (st.vectors), которые могли быть
    # начислены через apply_weights напрямую
    if vectors:
        for k, v in vectors.items():
            if k in ("G", "S", "T", "K"):
                vec[k] += float(v)
            elif k.startswith("mod_"):
                if k not in sums or sums[k] == 0:
                    sums[k] += float(v)

    # ----- Вычисляем первичные и вторичные модификаторы -----
    # Если secondary моды уже набраны из ответов — используем их.
    # Если нет — выводим из векторов G/S/T/K пропорционально их вкладу.

    # Маппинг векторов в первичные моды
    VEC_TO_PRIMARY = {"G": "mod_head", "S": "mod_heart", "T": "mod_body", "K": "mod_creativity"}

    # Для каждого вектора, который > 0, выводим соответвующие моды
    for vec_key in ("G", "S", "T", "K"):
        vv = vec.get(vec_key, 0)
        if vv <= 0:
            continue

        # Первичный мод (head, heart, body, creativity)
        prime_mod = VEC_TO_PRIMARY[vec_key]
        if sums.get(prime_mod, 0) <= 0:
            sums[prime_mod] = vv

        # Вторичные моды для каждой доминанты
        if vec_key == "G":
            if sums.get("mod_theoretical", 0) <= 0 and sums.get("mod_practical", 0) <= 0:
                sums["mod_theoretical"] = vv * 0.6
                sums["mod_natural"] = vv * 0.4
            if sums.get("mod_macro", 0) <= 0 and sums.get("mod_micro", 0) <= 0:
                sums["mod_macro"] = vv * 0.5
            if sums.get("mod_humanitarian", 0) <= 0:
                pass  # humanitarian не выводится из G напрямую
        elif vec_key == "S":
            if sums.get("mod_positive", 0) <= 0 and sums.get("mod_negative", 0) <= 0:
                sums["mod_positive"] = vv * 0.6
                sums["mod_generator"] = vv * 0.5
            if sums.get("mod_emitter", 0) <= 0:
                sums["mod_emitter"] = vv * 0.3
        elif vec_key == "T":
            if sums.get("mod_athlete", 0) <= 0 and sums.get("mod_master", 0) <= 0:
                sums["mod_athlete"] = vv * 0.6
                sums["mod_risk"] = vv * 0.5
            if sums.get("mod_static", 0) <= 0:
                sums["mod_static"] = vv * 0.3
            if sums.get("mod_scenic", 0) <= 0:
                sums["mod_scenic"] = vv * 0.2
            if sums.get("mod_situational", 0) <= 0:
                sums["mod_situational"] = vv * 0.2
        elif vec_key == "K":
            if sums.get("mod_inventor", 0) <= 0 and sums.get("mod_aesthetic", 0) <= 0:
                sums["mod_inventor"] = vv * 0.6
                sums["mod_natural"] = vv * 0.4
            if sums.get("mod_scenic", 0) <= 0:
                sums["mod_scenic"] = vv * 0.3
            if sums.get("mod_situational", 0) <= 0:
                sums["mod_situational"] = vv * 0.2

    return {
        "raw": dict(sums)
    }
