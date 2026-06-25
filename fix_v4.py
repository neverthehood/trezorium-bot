f = open("src/main_dating.py", "r", encoding="utf-8")
lines = f.readlines()
f.close()

# h_start: lines 279-295 (index 278-294)
# Старый блок: с @router.message(CommandStart()) до send_question
# Заменяем с 278 по 295 (18 строк)

new_h_start = """@router.message(CommandStart())
async def h_start(m: Message):
    welcome = (
        \"\\U0001f44b *Trezorium* \\u2014 сокровищница твоей половинки.\\n\\n\"
        \"Я считаю, что каждый человек \\u2014 уникальное сокровище \"
        \"со своим типом мышления, чувств и энергии.\\n\"
        \"Большинство знакомств \\u2014 лотерея. Я хочу, чтобы это была точная наука.\\n\\n\"
        \"Я задам 12 вопросов, чтобы узнать твой типаж, и найду того, кто тебе подходит.\\n\\n\"
        \"Первые 200 пользователей \\u2014 *бесплатный доступ навсегда* \\U0001f389\"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=\"\\U0001f680 Начнём!\", callback_data=\"start_onboarding\")]]
    )
    await m.answer(welcome, reply_markup=keyboard, parse_mode=\"Markdown\")


"""

# Строки с 278 по 295
new_lines = []
for i, line in enumerate(lines):
    if i >= 278 and i <= 295:
        continue  # Пропускаем старый h_start
    new_lines.append(line)

# Вставляем новый h_start перед строкой 296 (которая была 296)
# Строка 296 - это @router.message(Command("help"))
new_lines.insert(278, new_h_start)

f = open("src/main_dating.py", "w", encoding="utf-8")
f.writelines(new_lines)
f.close()
print("h_start replaced")

# Теперь заменяем h_onboarding_text и ask_age на новый блок с callback
# Старый блок: @router.message(F.text & ~F.command) + h_onboarding_text + ask_age
# lines 375-433... но после вставки индексы сдвинулись
