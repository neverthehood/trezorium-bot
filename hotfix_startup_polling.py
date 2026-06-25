# hotfix_startup_polling.py — добавляет логирование, delete_webhook и гарантированный polling
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Импорт logging (если нет)
if "import logging" not in s:
    s = s.replace("import asyncio", "import asyncio\nimport logging")

# Функцию main переписываем на «надёжную»
pat = re.compile(r'(?ms)^async\s+def\s+main\s*\([^)]*\)\s*:\s*.*?(?=^\s*(?:async\s+def|def|@|class)\b|\Z)')
new_main = (
"async def main():\n"
"    from .config import cfg\n"
"    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')\n"
"    bot = Bot(cfg.BOT_TOKEN)\n"
"    # на всякий — выключим вебхук, чтобы включился long polling\n"
"    try:\n"
"        await bot.delete_webhook(drop_pending_updates=True)\n"
"    except Exception as e:\n"
"        logging.warning(f\"delete_webhook failed: {e}\")\n"
"    dp = Dispatcher()\n"
"    dp.include_router(router)\n"
"    print(\"Bot is starting... (polling)\")\n"
"    # разрешённые типы апдейтов из зарегистрированных хэндлеров\n"
"    allowed = dp.resolve_used_update_types()\n"
"    await dp.start_polling(bot, allowed_updates=allowed)\n"
)
s = pat.sub(new_main, s)

# Хвост запуска — аккуратно
s = re.sub(r'(?ms)^if\s+__name__\s*==\s*[\'\"]__main__[\'\"]\s*:\s*.*\Z',
           'if __name__ == "__main__":\n'
           '    import asyncio\n'
           '    asyncio.run(main())\n', s)

shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: main() переписан: logging + delete_webhook + polling.")
