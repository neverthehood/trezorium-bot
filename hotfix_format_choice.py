# hotfix_format_choice.py — добавляет выбор формата и команду /format
import pathlib, re
p=pathlib.Path("src/main.py"); s=p.read_text(encoding="utf-8")

# 1) ключ в состоянии
if "st.style" not in s:
    s=s.replace("class St(", "class St(", 1)

# 2) клавиатура формата
if "def kb_format" not in s:
    s=s.replace("def kb_volume", 
r"""def kb_format():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B
    return InlineKeyboardMarkup(inline_keyboard=[
        [B(text="Классика", callback_data="fmt:classic")],
        [B(text="Истории",  callback_data="fmt:story")],
    ])

def kb_volume""")

# 3) ask_format()
if "async def ask_format" not in s:
    s=s.replace("async def ask_volume", 
r"""async def ask_format(m, st):
    txt = ("Выбери формат вопросов:\n\n"
           "• Классика — короткие, чёткие ситуации.\n"
           "• Истории — развернутые мини-сюжеты с погружением.")
    await m.answer(txt, reply_markup=kb_format())

async def ask_volume""")

# 4) обработчик нажатий формата
if "async def set_format" not in s:
    s=s.replace("async def set_aud", 
r"""async def set_format(cb, st):
    # cb.data = fmt:classic|story
    st.style = cb.data.split(":")[1]
    await safe_answer(cb, "Ок")
    await ask_volume(cb.message, st)

async def set_aud""")

# 5) в /start после пола идём в ask_format вместо ask_volume (подстрахуемся ещё командой)
s=re.sub(r"await\s+ask_volume\((?:[^)]+)\)", "await ask_format(m, st)", s)

# 6) регистрируем хэндлеры
if "router.callback_query.register(set_format" not in s:
    s=s.replace("router.callback_query.register(set_volume", 
                "router.callback_query.register(set_format, F.data.startswith('fmt:'))\nrouter.callback_query.register(set_volume")

# 7) команда /format
if "async def cmd_format" not in s:
    s += r"""

@router.message(F.text.regexp(r'^/format$'))
async def cmd_format(m, state):
    st = await state.get_data() or {}
    class Obj: pass
    obj=Obj(); obj.__dict__.update(st)
    await ask_format(m, obj)
"""

p.write_text(s,encoding="utf-8"); print("OK: добавлен выбор формата и /format")
