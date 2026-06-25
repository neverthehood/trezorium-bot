# src/indotype_resolver.py
# Определение индотипа по накопленным модификаторам

from typing import Dict, List


def has(mods: Dict[str, float], key: str) -> bool:
    """Проверка, есть ли модификатор со значимым весом"""
    return mods.get(f"mod_{key}", 0) > 0


def score(mods: Dict[str, float], key: str) -> float:
    """Возвращает значение модификатора (0, если отсутствует)"""
    return float(mods.get(f"mod_{key}", 0))


def best_of(mods: Dict[str, float], keys: list) -> str:
    """Возвращает ключ модификатора с наибольшим значением из списка"""
    best_key = keys[0]
    best_val = 0
    for k in keys:
        v = score(mods, k)
        if v > best_val:
            best_val = v
            best_key = k
    return best_key


def resolve_indotype(mods_result: Dict[str, Dict[str, float]]) -> Dict[str, str]:
    """
    Определяет индотип по списку модификаторов.

    На вход получает структуру из compute_mods:
    {
        "raw": {
            "mod_head": 3,
            "mod_practical": 2,
            ...
        }
    }

    Возвращает словарь:
    {
        "code": "G2AB",
        "title": "Практик-естественник, эксплуататор",
        "description": "..."
    }
    """

    mods = mods_result.get("raw", {})

    # ---------- 1. Определяем главную доминанту ----------
    # Сравниваем силу первичных модификаторов

    dominants = [
        ("head", score(mods, "head")),
        ("heart", score(mods, "heart")),
        ("body", score(mods, "body")),
        ("creativity", score(mods, "creativity")),
    ]
    # Сортируем по убыванию и берём сильнейшую
    dominants.sort(key=lambda x: x[1], reverse=True)
    strongest = dominants[0]

    if strongest[1] > 0:
        dom_key = strongest[0]
        if dom_key == "head":
            return resolve_head(mods)
        elif dom_key == "heart":
            return resolve_heart(mods)
        elif dom_key == "body":
            return resolve_body(mods)
        elif dom_key == "creativity":
            return resolve_creativity(mods)

    # Если ничего явно не накопилось
    return {
        "code": "UNKNOWN",
        "title": "Индотип не определён",
        "description": "Недостаточно данных для точного определения индотипа."
    }


# ===================== ГОЛОВА (G) =====================

def resolve_head(mods: Dict[str, float]) -> Dict[str, str]:

    # Определяем преобладающий подтип по относительным значениям
    theoretical = score(mods, "theoretical")
    practical = score(mods, "practical")
    natural = score(mods, "natural")
    humanitarian = score(mods, "humanitarian")
    macro = score(mods, "macro")
    micro = score(mods, "micro")

    # Если нет ни одного вторичного мода — возвращаем G-?
    if theoretical == 0 and practical == 0 and natural == 0 and humanitarian == 0 and macro == 0 and micro == 0:
        return indotype("G-?",
            "Голова (уточнение требуется)",
            "Проявлена доминанта интеллекта, но не хватает уточняющих признаков."
        )

    # G1 – теоретик (theoretical >= practical)
    if theoretical >= practical:

        # G1A – естественник (natural >= humanitarian)
        if natural >= humanitarian:

            if macro >= micro:
                return indotype("G1AA",
                    "Теоретик-естественник, макро",
                    "Видит общую картину мира, склонен к глобальному мышлению и теоретическим моделям."
                )
            else:
                return indotype("G1AB",
                    "Теоретик-естественник, микро",
                    "Сосредоточен на деталях и точности, любит проверку гипотез и глубокий анализ."
                )

        # G1B – гуманитарий
        else:

            if macro >= micro:
                return indotype("G1BA",
                    "Теоретик-гуманитарий, мыслитель",
                    "Работает с идеями и смыслами, склонен к философскому и концептуальному мышлению."
                )
            else:
                return indotype("G1BB",
                    "Теоретик-гуманитарий, слово",
                    "Талант ясно формулировать сложные мысли, прирождённый популяризатор знаний."
                )

    # G2 – практик (practical > theoretical)
    else:

        # G2A – естественник
        if natural >= humanitarian:

            if macro >= micro:
                return indotype("G2AA",
                    "Практик-естественник, изобретатель",
                    "Любит создавать новые механизмы и практические решения."
                )
            else:
                return indotype("G2AB",
                    "Практик-естественник, эксплуататор",
                    "Мастер поддерживать и совершенствовать уже существующие системы."
                )

        # G2B – гуманитарий
        else:

            if macro >= micro:
                return indotype("G2BA",
                    "Практик-гуманитарий, литератор",
                    "Талант рассказчика, писателя и мастера слова."
                )
            else:
                return indotype("G2BB",
                    "Практик-гуманитарий, лингвист",
                    "Природная чуткость к языкам и текстам."
                )

    return indotype("G-?",
        "Голова (уточнение требуется)",
        "Проявлена доминанта интеллекта, но не хватает уточняющих признаков."
    )


# ===================== СЕРДЦЕ (S) =====================

def resolve_heart(mods: Dict[str, float]) -> Dict[str, str]:

    positive = score(mods, "positive")
    negative = score(mods, "negative")
    generator = score(mods, "generator")
    emitter = score(mods, "emitter")
    macro = score(mods, "macro")

    # Если нет ни одного вторичного мода — возвращаем S-?
    if positive == 0 and negative == 0 and generator == 0 and emitter == 0:
        return indotype("S-?",
            "Сердце (уточнение требуется)",
            "Яркая эмоциональная доминанта, но не хватает точности для финального типа."
        )

    # S1 – позитив (positive >= negative)
    if positive >= negative:

        if generator >= emitter:
            if macro > 0:
                return indotype("S1AA",
                    "Позитив-генератор, приват",
                    "Тёплый и верный человек, ориентирован на близкий круг."
                )
            return indotype("S1AB",
                "Позитив-генератор, социал",
                "Альтруист, стремится делать мир лучше и помогать людям."
            )
        else:
            if macro > 0:
                return indotype("S1BA",
                    "Позитив-эмиттер, манипулятор",
                    "Умеет вдохновлять и вести за собой."
                )
            return indotype("S1BB",
                "Позитив-эмиттер, цветок",
                "Создаёт вокруг атмосферу тепла и уюта."
            )

    # S2 – негатив (negative > positive)
    else:

        if generator >= emitter:
            if macro > 0:
                return indotype("S2AA",
                    "Негатив-генератор, приват",
                    "Высокая внутренняя мобилизация и собранность."
                )
            return indotype("S2AB",
                "Негатив-генератор, социо",
                "Лучше работает в одиночку, упорен и жёсток."
            )
        else:
            if macro > 0:
                return indotype("S2BA",
                    "Негатив-эмиттер, манипулятор",
                    "Жёсткий лидер, способный держать дисциплину."
                )
            return indotype("S2BB",
                "Негатив-эмиттер, цветок",
                "Обладает сильным, но жёстким обаянием."
            )

    return indotype("S-?",
        "Сердце (уточнение требуется)",
        "Яркая эмоциональная доминанта, но не хватает точности для финального типа."
    )


# ===================== ТЕЛО (T) =====================

def resolve_body(mods: Dict[str, float]) -> Dict[str, str]:

    athlete = score(mods, "athlete")
    master = score(mods, "master")
    risk = score(mods, "risk")
    static = score(mods, "static")
    scenic = score(mods, "scenic")
    situational = score(mods, "situational")
    macro = score(mods, "macro")
    micro = score(mods, "micro")

    # Если нет ни одного вторичного мода — возвращаем T-?
    if athlete == 0 and master == 0 and risk == 0 and static == 0 and scenic == 0 and situational == 0:
        return indotype("T-?",
            "Тело (уточнение требуется)",
            "Явная телесная доминанта, но не хватает деталей для точного типа."
        )

    if athlete >= master:
        # T1 – атлет
        if risk >= static and risk >= scenic and risk >= situational:
            return indotype("T1AA",
                "Атлет-спортсмен, риск",
                "Любит экстремальные ситуации и вызовы."
            )
        elif static >= risk and static >= scenic and static >= situational:
            return indotype("T1AB",
                "Атлет-спортсмен, статик",
                "Стабильный и аккуратный исполнитель."
            )
        elif scenic >= risk and scenic >= static and scenic >= situational:
            return indotype("T1BA",
                "Атлет-актер, сценик",
                "Талант к публичности и выступлениям."
            )
        else:
            return indotype("T1BB",
                "Атлет-актер, ситуативник",
                "Мастер импровизации и действия по обстоятельствам."
            )
    else:
        # T2 – мастер
        # T2A – бионик (естественно-научный уклон, natural)
        # T2B – пластик/полимер (гуманитарно-прикладной уклон, humanitarian)
        natural = score(mods, "natural")
        humanitarian = score(mods, "humanitarian")

        if natural >= humanitarian:
            if macro >= micro:
                return indotype("T2AA",
                    "Мастер-макро, бионик",
                    "Любит работать с крупными живыми формами."
                )
            else:
                return indotype("T2AB",
                    "Мастер-микро, бионик",
                    "Мастер точной работы с живыми системами на микроуровне."
                )
        else:
            if macro >= micro:
                return indotype("T2BA",
                    "Мастер-макро, пластик",
                    "Скульптор, архитектор — творец крупных материальных форм."
                )
            else:
                return indotype("T2BB",
                    "Мастер-микро, полимер",
                    "Ювелирная точность, работа с мелкими деталями и материалами."
                )

    return indotype("T-?",
        "Тело (уточнение требуется)",
        "Явная телесная доминанта, но не хватает деталей для точного типа."
    )


# ===================== КРЕАТИВНОСТЬ (K) =====================

def resolve_creativity(mods: Dict[str, float]) -> Dict[str, str]:

    inventor = score(mods, "inventor")
    aesthetic = score(mods, "aesthetic")
    theoretical = score(mods, "theoretical")
    practical = score(mods, "practical")
    natural = score(mods, "natural")
    humanitarian = score(mods, "humanitarian")
    scenic = score(mods, "scenic")
    situational = score(mods, "situational")
    static = score(mods, "static")
    macro = score(mods, "macro")
    micro = score(mods, "micro")

    # Если нет ни одного вторичного мода — возвращаем K-?
    if inventor == 0 and aesthetic == 0 and theoretical == 0 and practical == 0 and natural == 0 and humanitarian == 0 and scenic == 0:
        return indotype("K-?",
            "Креативность (уточнение требуется)",
            "Яркая творческая доминанта, но не хватает данных для точного типа."
        )

    if inventor >= aesthetic:
        # K1 – инвентор
        # K1A – теоретик-инвентор (theoretical >= practical)
        if theoretical >= practical:
            if natural >= humanitarian:
                return indotype("K1AA",
                    "Инвентор-теоретик, естественник",
                    "Революционер в точных науках."
                )
            else:
                return indotype("K1AB",
                    "Инвентор-теоретик, гуманитарий",
                    "Создатель новых социальных и гуманитарных идей."
                )
        # K1B – практик-инвентор (practical > theoretical)
        else:
            if macro >= micro:
                return indotype("K1BA",
                    "Инвентор-практик, макро",
                    "Инженер-изобретатель крупных систем и механизмов."
                )
            else:
                return indotype("K1BB",
                    "Инвентор-практик, микро",
                    "Мастер тонких технологий, схем и микромеханизмов."
                )
    else:
        # K2 – эстетик
        # K2A – кюнстлер / импрессионист (scenic == 0 или минимален)
        if scenic <= 0 or (scenic < situational and scenic < static):
            return indotype("K2AA",
                "Эстетик-кюнстлер",
                "Художник в классическом смысле этого слова."
            )
        # K2B – акционист (scenic доминирует)
        else:
            # K2BA – сценик (scenic + macro)
            # K2BB – полимер (scenic + micro или situational)
            if macro >= micro:
                return indotype("K2BA",
                    "Эстетик-акционист, сценик",
                    "Творец перформансов и художественных действий."
                )
            else:
                return indotype("K2BB",
                    "Эстетик-акционист, полимер",
                    "Художник-оформитель, мастер декораций и визуальных решений."
                )

    return indotype("K-?",
        "Креативность (уточнение требуется)",
        "Яркая творческая доминанта, но не хватает данных для точного типа."
    )


# Вспомогательная функция

def indotype(code: str, title: str, description: str) -> Dict[str, str]:
    return {
        "code": code,
        "title": title,
        "description": description
    }
