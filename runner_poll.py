from pathlib import Path
import asyncio, os, logging
from aiogram import Bot, Dispatcher
from src.config import cfg
from src.main import router
ROOT = Path(__file__).resolve().parent.parent

async def run_polling():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')
    bot = Bot(cfg.BOT_TOKEN)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning(f"delete_webhook failed: {e}")
    dp = Dispatcher()
    dp.include_router(router)
    print("Runner: starting polling…")
    allowed = dp.resolve_used_update_types()
    await dp.start_polling(bot, allowed_updates=allowed)

if __name__ == "__main__":
    asyncio.run(run_polling())
