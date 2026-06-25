import os

content = open("src/config.py", "r", encoding="utf-8").read()

old = """def _read_token() -> str:
    # Загружаем .env из корня проекта
    dotenv_path = ROOT / \".env\"
    token = \"\"
    if dotenv_path.exists():
        with dotenv_path.open(\"r\", encoding=\"utf-8\") as f:
            for line in f:
                line = line.strip()
                if line.startswith(\"BOT_TOKEN=\"):
                    token = line.split(\"=\", 1)[1].strip()
                    break
    # Резервный способ — token.txt в корне
    if not token:
        alt = ROOT / \"token.txt\"
        if alt.exists():
            token = alt.read_text(encoding=\"utf-8\").strip()
    print(\">> TOKEN USED:\", token)
    return token"""

new = '''def _read_token() -> str:
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
    return token'''

content = content.replace(old, new)
open("src/config.py", "w", encoding="utf-8").write(content)
print("OK")
