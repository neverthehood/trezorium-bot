import pathlib

content = pathlib.Path("src/main_dating.py").read_text("utf-8")

# Заменяем блок от @router.message(F.text & ~F.command) до @router.callback_query(F.data.startswith("ans:"))
# на новые обработчики

old_block = """@router.message(F.text & ~F.command)
async def h_onboarding_text(m: Message):
    \"\"\"Сбор пола, возраста и предпочтений до начала теста.\"\"\"
    st = _sessions.get(m.chat.id)
    if not st or not getattr(st, 'waiting_for', None):
        return

    if st.waiting_for == \"gender\":
        text = m.text.strip().lower()
        if text in (\"парень\", \"мужчина\", \"мужской\", \"м\", \"male\"):
            st.gender = \"M\"
            await m.answer(\"А кого ты ищешь? *Парня* или *Девушку*?\", parse_mode=\"Markdown\")
            st.waiting_for = \"looking_for\"
        elif text in (\"девушка\", \"женщина\", \"женский\", \"ж\", \"female\"):
            st.gender = \"F\"
            await m.answer(\"А кого ты ищешь? *Парня* или *Девушку*?\", parse_mode=\"Markdown\")
            st.waiting_for = \"looking_for\"
        else:
            await m.answer(\"Напиши *парень* или *девушка* \\U0001f60a\", parse_mode=\"Markdown\")
        return

    if st.waiting_for == \"looking_for\":
        text = m.text.strip().lower()
        if text in (\"парня\", \"парень\", \"мужчина\", \"м\", \"male\"):
            st.looking_for = \"M\"
            await ask_age(m, st)
        elif text in (\"девушку\", \"девушка\", \"женщина\", \"ж\", \"female\"):
            st.looking_for = \"F\"
            await ask_age(m, st)
        elif text in (\"обоих\", \"всех\", \"любого\", \"любую\", \"любых\"):
            st.looking_for = \"A\"
            await ask_age(m, st)
        else:
            await m.answer(\"Напиши *парня*, *девушку* или *обоих* \\U0001f60a\", parse_mode=\"Markdown\")
        return

    if st.waiting_for == \"age\":
        text = m.text.strip()
        try:
            age = int(text)
            if age < 18:
                await m.answer(\"\\u26a0\\ufe0f Trezorium \\u2014 приложение 18+.\")
                return
            if age > 120:
                await m.answer(\"\\U0001f60a Ну не может быть столько, напиши честно:\")
                return
            st.age = age
            st.waiting_for = None
            # Начинаем тест
            q = bank.questions[0]
            await send_question(m, st, q.id)
        except ValueError:
            await m.answer(\"Напиши число \\u2014 сколько тебе лет \\U0001f60a\")


async def ask_age(m, st):
    st.waiting_for = \"age\"
    await m.answer(
        \"\\U0001f9d1\\u200d\\U0001f393 *Сколько тебе лет?*\\n\\n\"
        \"Напиши число (например: 25)\",
        parse_mode=\"Markdown\"
    )"""

new_block = """@router.callback_query(F.data == \"start_onboarding\")
async def h_start_onboarding(cb: CallbackQuery):
    await safe_answer(cb)
    st = SessionState(chat_id=cb.message.chat.id)
    _sessions[cb.message.chat.id] = st
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=\"\\U0001f466 Парень\", callback_data=\"gender_M\")],
            [InlineKeyboardButton(text=\"\\U0001f467 Девушка\", callback_data=\"gender_F\")],
        ]
    )
    await cb.message.answer(\"\\U0001f9d1 *Ты парень или девушка?*\", reply_markup=keyboard, parse_mode=\"Markdown\")
    st.waiting_for = \"gender\"


@router.callback_query(F.data.startswith(\"gender_\"))
async def h_onboarding_gender(cb: CallbackQuery):
    await safe_answer(cb)
    st = _sessions.get(cb.message.chat.id)
    if not st:
        return
    
    gender = cb.data.split(\"_\")[1]
    st.gender = gender
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=\"\\U0001f466 Парня\", callback_data=\"looking_M\")],
            [InlineKeyboardButton(text=\"\\U0001f467 Девушку\", callback_data=\"looking_F\")],
            [InlineKeyboardButton(text=\"\\U0001f91d Обоих\", callback_data=\"looking_A\")],
        ]
    )
    await cb.message.answer(\"\\U0001f50d *Кого ты ищешь?*\", reply_markup=keyboard, parse_mode=\"Markdown\")
    st.waiting_for = \"looking_for\"


@router.callback_query(F.data.startswith(\"looking_\"))
async def h_onboarding_looking(cb: CallbackQuery):
    await safe_answer(cb)
    st = _sessions.get(cb.message.chat.id)
    if not st:
        return
    
    st.looking_for = cb.data.split(\"_\")[1]
    
    await cb.message.answer(
        \"\\U0001f9d1\\u200d\\U0001f393 *Сколько тебе лет?*\\n\\n\"
        \"Напиши число (например: 25)\",
        parse_mode=\"Markdown\"
    )
    st.waiting_for = \"age\"


@router.message(F.text & ~F.command)
async def h_onboarding_age(m: Message):
    \"\"\"Принимаем возраст текстом.\"\"\"
    st = _sessions.get(m.chat.id)
    if not st or getattr(st, 'waiting_for', None) != \"age\":
        return
    
    text = m.text.strip()
    try:
        age = int(text)
        if age < 18:
            await m.answer(\"\\u26a0\\ufe0f Trezorium \\u2014 приложение 18+.\")
            return
        if age > 120:
            await m.answer(\"\\U0001f60a Ну не может быть столько, напиши честно:\")
            return
        st.age = age
        st.waiting_for = None
        # Начинаем тест
        q = bank.questions[0]
        await send_question(m, st, q.id)
    except ValueError:
        await m.answer(\"Напиши число \\u2014 сколько тебе лет \\U0001f60a\")"""

content = content.replace(old_block, new_block)

pathlib.Path("src/main_dating.py").write_text(content, "utf-8")
print("OK")
print("gender_M:", "gender_M" in content)
print("looking_A:", "looking_A" in content)
