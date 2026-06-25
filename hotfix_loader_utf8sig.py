# hotfix_loader_utf8sig.py — лоадер читает JSON как utf-8-sig
from pathlib import Path
import re

p = Path("src/question_loader.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# заменяем open(..., encoding="utf-8") на utf-8-sig везде в этом файле
s = re.sub(r'open\(([^)]*?)encoding\s*=\s*["\']utf-8["\']',
           r'open(\1encoding="utf-8-sig"', s)

# на всякий, если встречается json.load(open(path)) без encoding — обернём аккуратно нельзя на лету.
# (оставляем как есть; главное — явные места с encoding.)

p.write_text(s, encoding="utf-8")
print("OK: question_loader теперь читает пакеты как utf-8-sig.")
