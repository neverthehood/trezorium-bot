# hotfix_short_card_guard.py
from pathlib import Path
import re

p = Path("src/main.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'short = render_short_card(code)\n        await m.answer(short)',
    'short = render_short_card(code)\n        if code and code != "—":\n            await m.answer(short)'
)
p.write_text(s, encoding="utf-8")
print("OK: короткая карточка — только при валидном коде.")
