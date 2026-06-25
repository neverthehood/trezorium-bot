#!/usr/bin/env python3
"""Создаёт pack_dating_v1.json — 12 вопросов для знакомств."""
import json
from pathlib import Path

PACKS = Path(__file__).parent.parent / "data" / "packs"

questions = [
    {
        "id": "1",
        "format": "single",
        "text": "Твой идеальный вечер — это...",
        "options": [
            {"id": "A", "label": "Лежать с книгой или смотреть научпоп", "weights": {"mod_theoretical": 3, "mod_intro": 3, "mod_static": 2}},
            {"id": "B", "label": "Шумная вечеринка с друзьями", "weights": {"mod_extro": 3, "mod_positive": 2, "mod_scenic": 2}},
            {"id": "C", "label": "Поход в горы с палаткой", "weights": {"mod_natural": 3, "mod_athlete": 2, "mod_risk": 2}},
            {"id": "D", "label": "Мастерить/ремонтировать что-то руками", "weights": {"mod_practical": 3, "mod_master": 2, "mod_intro": 1}}
        ]
    },
    {
        "id": "2",
        "format": "single",
        "text": "Коллега предлагает рискованный проект. Ты...",
        "options": [
            {"id": "A", "label": "Сначала всё просчитаю, потом решу", "weights": {"mod_theoretical": 2, "mod_planned": 3, "mod_static": 2}},
            {"id": "B", "label": "Горю идеей, хочу попробовать!", "weights": {"mod_risk": 3, "mod_spontaneous": 2, "mod_extro": 2}},
            {"id": "C", "label": "Посмотрю, что скажет команда", "weights": {"mod_heart": 2, "mod_positive": 2, "mod_negative": 1}},
            {"id": "D", "label": "Предложу свой альтернативный план", "weights": {"mod_inventor": 3, "mod_practical": 2, "mod_head": 2}}
        ]
    },
    {
        "id": "3",
        "format": "single",
        "text": "Твой друг расстроен. Твои действия?",
        "options": [
            {"id": "A", "label": "Обниму и выслушаю", "weights": {"mod_heart": 3, "mod_positive": 2, "mod_intro": 2}},
            {"id": "B", "label": "Предложу решение проблемы", "weights": {"mod_head": 3, "mod_practical": 2, "mod_planned": 1}},
            {"id": "C", "label": "Позову гулять/развеяться", "weights": {"mod_extro": 3, "mod_athlete": 1, "mod_scenic": 2}},
            {"id": "D", "label": "Расскажу анекдот, чтобы отвлечь", "weights": {"mod_positive": 3, "mod_spontaneous": 2, "mod_emitter": 2}}
        ]
    },
    {
        "id": "4",
        "format": "single",
        "text": "Что тебя больше всего привлекает в людях?",
        "options": [
            {"id": "A", "label": "Ум, эрудиция, необычные идеи", "weights": {"mod_theoretical": 3, "mod_head": 2, "mod_inventor": 1}},
            {"id": "B", "label": "Доброта, забота, умение слушать", "weights": {"mod_heart": 3, "mod_positive": 3, "mod_generator": 1}},
            {"id": "C", "label": "Активность, энергия, страсть к жизни", "weights": {"mod_athlete": 2, "mod_extro": 2, "mod_risk": 2}},
            {"id": "D", "label": "Креативность, чувство юмора", "weights": {"mod_inventor": 2, "mod_aesthetic": 2, "mod_spontaneous": 2}}
        ]
    },
    {
        "id": "5",
        "format": "single",
        "text": "Как ты планируешь отпуск?",
        "options": [
            {"id": "A", "label": "Расписываю всё по дням за месяц", "weights": {"mod_planned": 3, "mod_static": 2, "mod_theoretical": 1}},
            {"id": "B", "label": "Покупаю билет и решаю на месте", "weights": {"mod_spontaneous": 3, "mod_risk": 2, "mod_extro": 1}},
            {"id": "C", "label": "Еду к друзьям/родственникам", "weights": {"mod_heart": 2, "mod_positive": 2, "mod_emitter": 2}},
            {"id": "D", "label": "Ищу необычное — волонтёрство, ретрит", "weights": {"mod_natural": 2, "mod_inventor": 2, "mod_aesthetic": 2}}
        ]
    },
    {
        "id": "6",
        "format": "single",
        "text": "Твой главный страх в отношениях?",
        "options": [
            {"id": "A", "label": "Что меня не поймут, не оценят ум", "weights": {"mod_theoretical": 2, "mod_head": 2, "mod_negative": 2}},
            {"id": "B", "label": "Что меня будут использовать", "weights": {"mod_heart": 2, "mod_negative": 2, "mod_generator": 1}},
            {"id": "C", "label": "Что будет скучно и однообразно", "weights": {"mod_risk": 2, "mod_spontaneous": 2, "mod_extro": 2}},
            {"id": "D", "label": "Что потеряю свободу и себя", "weights": {"mod_inventor": 2, "mod_aesthetic": 2, "mod_emitter": 2}}
        ]
    },
    {
        "id": "7",
        "format": "single",
        "text": "Выбери цитату, которая тебе ближе:",
        "options": [
            {"id": "A", "label": "«Порядок освобождает мысль»", "weights": {"mod_planned": 3, "mod_theoretical": 2, "mod_head": 1}},
            {"id": "B", "label": "«Жизнь — то, что происходит, пока строишь планы»", "weights": {"mod_spontaneous": 3, "mod_risk": 2, "mod_positive": 1}},
            {"id": "C", "label": "«Самое главное — люди рядом»", "weights": {"mod_heart": 3, "mod_positive": 2, "mod_emitter": 2}},
            {"id": "D", "label": "«Творчество — единственный способ сбежать»", "weights": {"mod_inventor": 3, "mod_aesthetic": 2, "mod_spontaneous": 1}}
        ]
    },
    {
        "id": "8",
        "format": "single",
        "text": "Твой стиль в одежде?",
        "options": [
            {"id": "A", "label": "Классика, удобство, ничего лишнего", "weights": {"mod_static": 3, "mod_planned": 2, "mod_theoretical": 1}},
            {"id": "B", "label": "Ярко, модно, чтобы заметили", "weights": {"mod_scenic": 3, "mod_extro": 2, "mod_emitter": 2}},
            {"id": "C", "label": "Практично — главное не мешает", "weights": {"mod_practical": 3, "mod_natural": 2, "mod_athlete": 1}},
            {"id": "D", "label": "Самовыражение, винтаж, эклектика", "weights": {"mod_aesthetic": 3, "mod_inventor": 2, "mod_spontaneous": 2}}
        ]
    },
    {
        "id": "9",
        "format": "single",
        "text": "Что тебя вдохновляет?",
        "options": [
            {"id": "A", "label": "Научные открытия, книги, лекции", "weights": {"mod_theoretical": 3, "mod_head": 2, "mod_macro": 2}},
            {"id": "B", "label": "Люди, их истории, эмоции", "weights": {"mod_heart": 3, "mod_positive": 2, "mod_emitter": 2}},
            {"id": "C", "label": "Природа, путешествия, спорт", "weights": {"mod_natural": 3, "mod_athlete": 2, "mod_risk": 1}},
            {"id": "D", "label": "Искусство, музыка, красивые вещи", "weights": {"mod_aesthetic": 3, "mod_inventor": 2, "mod_scenic": 2}}
        ]
    },
    {
        "id": "10",
        "format": "single",
        "text": "Твой девиз по жизни:",
        "options": [
            {"id": "A", "label": "«Семь раз отмерь — один раз отрежь»", "weights": {"mod_planned": 3, "mod_static": 2, "mod_theoretical": 2}},
            {"id": "B", "label": "«Кто не рискует — тот не пьёт шампанское»", "weights": {"mod_risk": 3, "mod_spontaneous": 2, "mod_extro": 2}},
            {"id": "C", "label": "«Относись к другим как к себе»", "weights": {"mod_heart": 3, "mod_positive": 2, "mod_generator": 2}},
            {"id": "D", "label": "«Будь собой, остальные уже заняты»", "weights": {"mod_inventor": 2, "mod_aesthetic": 2, "mod_emitter": 2}}
        ]
    },
    {
        "id": "11",
        "format": "single",
        "text": "Как ты ведёшь себя в конфликте?",
        "options": [
            {"id": "A", "label": "Логически объясняю свою позицию", "weights": {"mod_head": 3, "mod_theoretical": 2, "mod_planned": 1}},
            {"id": "B", "label": "Стараюсь сгладить и сохранить отношения", "weights": {"mod_heart": 3, "mod_positive": 2, "mod_negative": 1}},
            {"id": "C", "label": "Могу вспылить, но быстро отхожу", "weights": {"mod_negative": 2, "mod_extro": 2, "mod_emitter": 2}},
            {"id": "D", "label": "Замолкаю и ухожу в себя", "weights": {"mod_intro": 3, "mod_negative": 1, "mod_static": 2}}
        ]
    },
    {
        "id": "12",
        "format": "single",
        "text": "Что ты ищешь в отношениях?",
        "options": [
            {"id": "A", "label": "Партнёра для интеллектуальных бесед", "weights": {"mod_theoretical": 2, "mod_head": 2, "mod_macro": 2}},
            {"id": "B", "label": "Теплоту, заботу и безопасность", "weights": {"mod_heart": 3, "mod_positive": 2, "mod_static": 2}},
            {"id": "C", "label": "Приключений и ярких эмоций", "weights": {"mod_risk": 3, "mod_extro": 2, "mod_spontaneous": 2}},
            {"id": "D", "label": "Вдохновения и взаимного творчества", "weights": {"mod_inventor": 2, "mod_aesthetic": 2, "mod_emitter": 2}}
        ]
    }
]

pack = {
    "meta": {
        "name": "Trezorium Dating",
        "version": "1.0",
        "audience": "adult",
        "style": "story",
        "description": "Короткий тест для знакомств — 12 вопросов"
    },
    "features": {},
    "questions": questions
}

PACKS.mkdir(parents=True, exist_ok=True)
path = PACKS / "pack_dating_v1.json"
path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Created: {path} ({len(questions)} questions)")
