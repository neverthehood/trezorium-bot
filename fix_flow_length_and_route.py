# fix_flow_length_and_route.py — чинит цепочку выбора объёма → старт вопросов
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = (s.replace("\","").replace("\ "," ").replace("\r","").replace("\t","    "))

# 1) Нормализуем kb_length()
kb_pat = re.compile(r'(?ms)^def\s+kb_length\s*\(\)\s*:\s*.*?(?=^\s*(?:def|async\s+def|@|class)\b|\Z)')
kb_block = (
    "def kb_length():\n"
    "    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as B\n"
    "    return InlineKeyboardMarkup(inline_keyboard=[\n"
    "        [B(text=\"Экспресс (коротко)\", callback_data=\"len:express\")],\n"
    "        [B(text=\"Стандарт (сбалансировано)\", callback_data=\"len:standard\")],\n"
    "        [B(text=\"Глубоко (подробно)\", callback_data=\"len:deep\")],\n"
    "    ])\n"
    "\n"
)
if kb_pat.search(s):
    s = kb_pat.sub(kb_block, s)
else:
    # если kb_length нет — добавим рядом с kb_format
    s = re.sub(r'(?m)^def\s+kb_format\s*\(\)\s*:\s*.*?\n\n',
               lambda m: m.group(0) + kb_block, s)

# 2) Укрепим _plan_and_start: fallback если маршрут пуст
plan_pat = re.compile(r'(?ms)^\s*def\s+_plan_and_start\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
def add_fallback(body: str) -> str:
    if "route_core" in body and "if not getattr(st, 'route_core', None)" in body:
        return body  # уже патчено ранее
    insert = (
        "    # если по выбранным параметрам маршрут пуст — попробуем альтернативный формат\n"
        "    if not getattr(st, 'route_core', None):\n"
        "        alt = 'classic' if st.style == 'story' else 'story'\n"
        "        try:\n"
        "            st.route_core = build_route(sample_n, chat_id, st.mode, alt)\n"
        "            st.style = alt if st.route_core else st.style\n"
        "        except Exception:\n"
        "            pass\n"
    )
    # вставим перед return 'Начинаем!'
    return re.sub(r"(return\s+['\"])Начинаем!(['\"])",
                  insert + r"\n    return 'Начинаем!'", body, count=1)

if plan_pat.search(s):
    body = plan_pat.search(s).group(0)
    body_new = add_fallback(body)
    s = s.replace(body, body_new)

# 3) Полностью перепишем set_length с отладочным логом и явным стартом
setlen_pat = re.compile(r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("len:"\)\)\s*?\n\s*async\s+def\s+set_length\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:@|async\s+def|def|class)\b|\Z)')
setlen_block = (
    "@router.callback_query(F.data.startswith(\"len:\"))\n"
    "async def set_length(cb: CallbackQuery):\n"
    "    _, val = cb.data.split(\":\", 1)\n"
    "    st = st_for(cb.message.chat.id)\n"
    "    st.length = val if val in (\"express\",\"standard\",\"deep\") else \"standard\"\n"
    "    await safe_answer(cb, \"Объём выбран\")\n"
    "    # Диагностика\n"
    "    print(f\"[DEBUG] set_length: length={st.length} mode={getattr(st,'mode',None)} style={getattr(st,'style',None)}\")\n"
    "    intro = _plan_and_start(cb, st)\n"
    "    # если по какой-то причине маршрут не собрался — скажем об этом\n"
    "    if not getattr(st, 'route_core', None):\n"
    "        await cb.message.answer(\"Пока не нашлось вопросов для выбранных настроек. Попробуй другой формат/объём.\")\n"
    "        return\n"
    "    print(f\"[DEBUG] route size: {len(st.route_core)}\")\n"
    "    await cb.message.answer(intro)\n"
    "    # старт — первый вопрос\n"
    "    try:\n"
    "        first_id = st.route_core[0]\n"
    "    except Exception:\n"
    "        await cb.message.answer(\"Маршрут пуст. Попробуй другой формат/объём.\")\n"
    "        return\n"
    "    await send_q(cb.message, st, first_id)\n"
    "\n"
)
if setlen_pat.search(s):
    s = setlen_pat.sub(setlen_block, s)
else:
    # если не нашли — добавим рядом с обработчиком gender
    s = re.sub(r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\(\"gender:\"\)\)\s*?\n\s*async\s+def\s+set_gender\s*\([^)]*\)\s*:\s*.*?\n\n',
               lambda m: m.group(0) + setlen_block, s)

# 4) На всякий: убедимся, что декораторы все через router
s = re.sub(r'(?m)^(\s*)@dp\.(message|callback_query)\(', r'\1@router.\2(', s)

shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: kb_length нормализован, _plan_and_start получил fallback, set_length переписан и логирует шаги.")
