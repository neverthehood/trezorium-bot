import pathlib

f = pathlib.Path("src/main_dating.py")
content = f.read_text("utf-8")

# Ищем уникальную строку из h_start - "Меня зовут *Trezorium*"
if 'Меня зовут *Trezorium*' in content:
    # Находим блок от @router.message(CommandStart()) до @router.message(Command("help"))
    import re
    # Убираем старый h_start и вставляем новый
    old = '''@router.message(CommandStart())
async def h_start(m: Message):
    welcome = (
        "Привет! \U0001f44b\\n\\n"
        "Меня зовут *Trezorium*.\\n\\n"
        "\u00abTrezorium\u00bb \u2014 это сокровищница. Я считаю, что каждый человек \u2014 уникальное сокровище "
        "со своим типом мышления, чувств и энергии. Большинство знакомств \u2014 это лотерея. "
        "Я хочу, чтобы это была точная наука.\\n\\n"
        "Я задам 12 вопросов, чтобы узнать твой типаж, и найду того, кто тебе подходит.\\n\\n"
        "Первые 200 пользователей \u2014 *бесплатный доступ навсегда* \U0001f389\\n\\n"
        "\u041f\u043e\u0435\u0445\u0430\u043b\u0438?"
    )
    await m.answer(welcome, parse_mode="Markdown")

    st = SessionState(chat_id=m.chat.id)
    _sessions[m.chat.id] = st

    q = bank.questions[0]
    await send_question(m, st, q.id)'''
    
    new = '''@router.message(CommandStart())
async def h_start(m: Message):
    welcome = (
        "\U0001f44b *Trezorium* \u2014 сокровищница твоей половинки.\\n\\n"
        "Я считаю, что каждый человек \u2014 уникальное сокровище "
        "со своим типом мышления, чувств и энергии.\\n"
        "Большинство знакомств \u2014 лотерея. Я хочу, чтобы это была точная наука.\\n\\n"
        "Я задам 12 вопросов, чтобы узнать твой типаж, и найду того, кто тебе подходит.\\n\\n"
        "Первые 200 пользователей \u2014 *бесплатный доступ навсегда* \U0001f389"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="\U0001f680 Начнём!", callback_data="start_onboarding")]]
    )
    await m.answer(welcome, reply_markup=keyboard, parse_mode="Markdown")'''
    
    content = content.replace(old, new)
    f.write_text(content, "utf-8")
    print("h_start replaced")
else:
    print("Old h_start not found")

# Проверяем
content2 = f.read_text("utf-8")
print("start_onboarding count:", content2.count("start_onboarding"))
