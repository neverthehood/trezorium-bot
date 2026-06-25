# src/gpt_messages.py
# GPT-генерация первого сообщения для мэтча

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from src.legal import AGREEMENT_TEXT
import aiohttp

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")

TYPE_NAMES = {
    "G1AA": "Профессор", "G1AB": "Лаборант", "G1BA": "Философ", "G1BB": "Писатель",
    "G2AA": "Инженер", "G2AB": "Механик", "G2BA": "Блогер", "G2BB": "Полиглот",
    "S1AA": "Романтик", "S1AB": "Альтруист", "S1BA": "Лидер", "S1BB": "Душа компании",
    "S2AA": "Перфекционист", "S2AB": "Рекордсмен", "S2BA": "Воин", "S2BB": "Роковая личность",
    "T1AA": "Экстремал", "T1AB": "Марафонец", "T1BA": "Артист", "T1BB": "Спасатель",
    "T2AA": "Садовник", "T2AB": "Строитель", "T2BA": "Музыкант", "T2BB": "Ювелир",
    "K1AA": "Изобретатель", "K1AB": "Проводник", "K1BA": "Мастер-самоделкин", "K1BB": "Бионик",
    "K2AA": "Художник", "K2AB": "Скульптор", "K2BA": "Режиссёр", "K2BB": "Бунтарь",
}

async def generate_first_message(
    code_a: str,
    mods_a: Dict[str, float],
    code_b: str,
    mods_b: Dict[str, float],
    score: float
) -> str:
    """
    Генерирует первое сообщение для мэтча через GPT.
    
    Промпт построен так, чтобы сообщение было:
    - дружелюбным, с юмором
    - показывало знание обоих типажей
    - давало конкретную тему для разговора
    """
    
    name_a = TYPE_NAMES.get(code_a, code_a)
    name_b = TYPE_NAMES.get(code_b, code_b)
    
    # Собираем ключевые моды для обоих
    top_mods_a = sorted(mods_a.items(), key=lambda x: -abs(x[1]))[:5]
    top_mods_b = sorted(mods_b.items(), key=lambda x: -abs(x[1]))[:5]
    
    mods_a_str = ", ".join(f"{k}={v:.1f}" for k, v in top_mods_a)
    mods_b_str = ", ".join(f"{k}={v:.1f}" for k, v in top_mods_b)
    
    prompt = f"""Ты — дружелюбный помощник сервиса знакомств Trezorium.
Напиши короткое (2-4 предложения) первое сообщение для пары, которая только что получила мэтч.

Обращайся к первому человеку (А). Он/она видит результат.

Данные:
• Тип А: {name_a} ({code_a}), моды: {mods_a_str}
• Тип Б: {name_b} ({code_b}), моды: {mods_b_str}
• Совместимость: {score:.0f}%

Сообщение должно:
1. Быть дружелюбным и с лёгким юмором
2. Объяснять, почему они совместимы (на основе модов)
3. Предлагать конкретную тему для начала диалога
4. Не быть слишком длинным
5. Начинаться с обращения "Ты"
6. Использовать русский язык

Пример:
"Ты — Профессор, любишь во всём разбираться досконально. А твой мэтч — Бунтарь, который обожает нарушать правила. Звучит как начало отличного интеллектуального детектива! Спроси у него/неё, что он/она думает о квантовой механике — гарантирую, ответ будет неожиданным."
"""
    
    if not OPENAI_KEY:
        # Fallback, если нет API ключа
        return (
            f"🎯 Вы совместимы на {score:.0f}%!\n"
            f"Ты — {name_a}, он/она — {name_b}. "
            f"Попробуйте обсудить, что вас привело в Trezorium — это всегда хорошее начало 😉"
        )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Ты — дружелюбный помощник сервиса знакомств. Отвечай коротко, с юмором, по-русски."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.8,
                }
            ) as resp:
                data = await resp.json()
                msg = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if msg:
                    return msg
    except Exception as e:
        print(f"[GPT] Error: {e}")
    
    return (
        f"🎯 Вы совместимы на {score:.0f}%!\n"
        f"Ты — {name_a}, а он/она — {name_b}. "
        f"У вас отличный потенциал — напишите друг другу!"
    )
