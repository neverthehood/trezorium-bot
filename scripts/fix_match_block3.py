import sys
sys.path.insert(0, '.')

with open('src/main_dating.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Найдём блок
start = content.find('async def delayed_match_notify')
end = content.find('_bot_instance = None') + len('_bot_instance = None')

old_block = content[start:end]

# Читаем новый блок из отдельного файла, чтобы избежать проблем с f-строками
new_block = """async def delayed_match_notify(chat_id: int, code: str, mods_raw: dict, delay_sec: int):
    \"\"\"Через delay_sec секунд найти мэтч и отправить уведомление.\"\"\"
    import logging
    logger = logging.getLogger(__name__)

    await asyncio.sleep(delay_sec)

    try:
        bot = _bot_instance
        if not bot:
            return
        match = await find_match(chat_id, code, mods_raw)
        if match:
            match_user_id, match_code, _, score = match
            match_name = TYPE_NAMES.get(match_code, match_code)
            text = (
                f\"\\U0001f3af *Мы нашли твою половинку!*\\n\\n\"
                f\"Совместимость: *{score:.0f}%*\\n\"
                f\"Типаж: {match_name}\\n\\n\"
                f\"Нажми на кнопку ниже, чтобы написать \\U0001f447\"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=\"\\U0001f4ac Написать\", url=f\"tg://user?id={match_user_id}\")]
                ]
            )
            await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode=\"Markdown\")
            logger.info(f\"Match notification sent to {chat_id}: {match_code} (user_id={match_user_id})\")
        else:
            logger.info(f\"Match not found for {chat_id} after delay, will retry later\")
            asyncio.create_task(delayed_match_notify(chat_id, code, mods_raw, 24 * 3600))
    except Exception as e:
        logger.error(f\"Match notification error for {chat_id}: {e}\")
        asyncio.create_task(delayed_match_notify(chat_id, code, mods_raw, 3600))


_bot_instance = None"""

content = content[:start] + new_block + content[end:]

with open('src/main_dating.py', 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
py_compile.compile('src/main_dating.py', doraise=True)
print('Syntax OK')
