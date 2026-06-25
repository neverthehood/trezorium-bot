from pathlib import Path
# src/config.py — простой и надёжный лоадер токена
import os
from dataclasses import dataclass
ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv()  # загрузит .env из корня проекта
except Exception:
    pass

def _read_token() -> str:
    # 1. Сначала переменные окружения (Render, хостинг)
    token = os.getenv("BOT_TOKEN", "")
    if token:
        return token
    # 2. Загружаем .env из корня проекта (локальная разработка)
    dotenv_path = ROOT / ".env"
    if dotenv_path.exists():
        with dotenv_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break
    # 3. Резервный способ - token.txt в корне
    if not token:
        alt = ROOT / "token.txt"
        if alt.exists():
            token = alt.read_text(encoding="utf-8").strip()
    return token

@dataclass
class Config:
    BOT_TOKEN: str = _read_token()
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

cfg = Config()
