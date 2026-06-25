# src/matcher.py
# Алгоритм совместимости (matchmaking) на основе теории Trezorium

from typing import Dict, List, Tuple

# Веса осей для совместимости
AXIS_WEIGHTS = {
    # Социальность (20%)
    "extro": 0.10,
    "intro": 0.10,
    
    # Стиль мышления (15%)
    "theoretical": 0.075,
    "natural": 0.075,
    
    # Планирование (10%)
    "planned": 0.05,
    "spontaneous": 0.05,
    
    # Эмоциональный фон (10%)
    "positive": 0.05,
    "negative": 0.05,
    
    # Риск/статика (10%)
    "risk": 0.05,
    "static": 0.05,
    
    # Стиль влияния (10%)
    "generator": 0.05,
    "emitter": 0.05,
    
    # Первичные векторы (25%)
    "head": 0.0625,
    "heart": 0.0625,
    "body": 0.0625,
    "creativity": 0.0625,
}

# Пары модов, которые считаются "противоположными"
# Для них важна НЕ разница, а дополнение
COMPLEMENTARY_PAIRS = [
    ("extro", "intro"),
    ("theoretical", "natural"),
    ("planned", "spontaneous"),
    ("positive", "negative"),
    ("risk", "static"),
    ("generator", "emitter"),
    ("head", "heart"),
    ("head", "body"),
    ("head", "creativity"),
    ("heart", "body"),
    ("heart", "creativity"),
    ("body", "creativity"),
]

# Пары, где важно СХОДСТВО
SIMILAR_PAIRS = [
    ("head", "head"),
    ("heart", "heart"),
    ("body", "body"),
    ("creativity", "creativity"),
    ("extro", "extro"),
    ("intro", "intro"),
    ("theoretical", "theoretical"),
    ("natural", "natural"),
    ("planned", "planned"),
    ("spontaneous", "spontaneous"),
]


def compute_match(mods_a: Dict[str, float], mods_b: Dict[str, float]) -> float:
    """
    Считает процент совместимости между двумя профилями (0-100%).
    
    Логика:
    - Для complementary пар: идеал — среднее значение (оба выражены, но не крайности)
    - Для similar пар: идеал — близкие значения
    - Для первичных векторов: дополнение (head+heart = баланс)
    """
    
    score = 0.0
    total_weight = 0.0
    
    # 1. Сходство по одинаковым модам
    for mod_key in AXIS_WEIGHTS:
        weight = AXIS_WEIGHTS[mod_key]
        va = mods_a.get(mod_key, 0)
        vb = mods_b.get(mod_key, 0)
        max_val = max(abs(va), abs(vb), 1)
        
        # Чем ближе — тем выше балл
        similarity = 1.0 - abs(va - vb) / max_val
        score += weight * similarity
        total_weight += weight
    
    # 2. Дополнение по первичным векторам
    # Если у A high head, а у B high heart — бонус
    primary_keys = ["head", "heart", "body", "creativity"]
    for i in range(len(primary_keys)):
        for j in range(i + 1, len(primary_keys)):
            k1, k2 = primary_keys[i], primary_keys[j]
            v1a, v1b = mods_a.get(k1, 0), mods_a.get(k2, 0)
            v2a, v2b = mods_b.get(k1, 0), mods_b.get(k2, 0)
            
            # Дополнение: у A k1 > k2, у B k2 > k1
            if (v1a > v1b and v2b > v2a) or (v1b > v1a and v2a > v2b):
                bonus = 0.03 * (abs(v1a - v1b) / max(abs(v1a), abs(v1b), 1))
                score += bonus
                total_weight += bonus
    
    # Нормализация
    if total_weight > 0:
        score = (score / total_weight) * 100.0
    
    return min(100.0, max(0.0, score))


def get_explanation(mods_a: Dict[str, float], mods_b: Dict[str, float]) -> List[str]:
    """Генерирует текстовое объяснение, почему пользователи совместимы."""
    explanations = []
    
    # Проверяем первичные векторы
    primaries = ["head", "heart", "body", "creativity"]
    dom_a = max(primaries, key=lambda k: mods_a.get(k, 0))
    dom_b = max(primaries, key=lambda k: mods_b.get(k, 0))
    
    dom_names = {
        "head": "Голова (анализ)",
        "heart": "Сердце (эмпатия)",
        "body": "Тело (действие)",
        "creativity": "Креатив (творчество)"
    }
    
    if dom_a != dom_b:
        explanations.append(
            f"Ты — {dom_names.get(dom_a, dom_a)}, "
            f"а твой мэтч — {dom_names.get(dom_b, dom_b)}. "
            "Вы отлично дополняете друг друга!"
        )
    else:
        explanations.append(
            f"У вас обоих доминирует {dom_names.get(dom_a, dom_a)}. "
            "Вы понимаете друг друга с полуслова."
        )
    
    # Проверяем социальность
    extro_a = mods_a.get("extro", 0)
    intro_a = mods_a.get("intro", 0)
    extro_b = mods_b.get("extro", 0)
    intro_b = mods_b.get("intro", 0)
    
    if extro_a > intro_a and extro_b > intro_b:
        explanations.append("Оба экстраверты — вам никогда не будет скучно вдвоём!")
    elif intro_a > extro_a and intro_b > extro_b:
        explanations.append("Оба интроверты — вы будете лучшей парой для уютных вечеров.")
    else:
        explanations.append("Один экстраверт, другой интроверт — классика. Он/она вытащит тебя в люди, а ты поможешь замедлиться.")
    
    # Стиль мышления
    theo_a = mods_a.get("theoretical", 0)
    nat_a = mods_a.get("natural", 0)
    theo_b = mods_b.get("theoretical", 0)
    nat_b = mods_b.get("natural", 0)
    
    if abs(theo_a - theo_b) < 2 and abs(nat_a - nat_b) < 2:
        explanations.append("У вас похожий стиль мышления — вы найдёте общий язык в любом споре.")
    else:
        explanations.append("Вы мыслите по-разному, и это здорово: один видит общую картину, другой — детали.")
    
    return explanations
