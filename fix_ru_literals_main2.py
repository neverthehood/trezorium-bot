# fix_ru_literals_main2.py — чинит оставшиеся русские литералы в src/main.py
from pathlib import Path

p = Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\","")

repls = {
    "Р’С‹Р±РµСЂРё: С‡С‚Рѕ *Р±Р»РёР¶Рµ РІСЃРµРіРѕ С‚РµР±Рµ*": "Выбери: что *ближе всего тебе*",
    "РўРµРїРµСЂСЊ РІС‹Р±РµСЂРё: С‡С‚Рѕ *РјРµРЅСЊС€Рµ РІСЃРµРіРѕ РїСЂРѕ С‚РµР±СЏ*": "Теперь выбери: что *меньше всего про тебя*"
}

fixed = 0
for bad, good in repls.items():
    if bad in s:
        s = s.replace(bad, good); fixed += 1

p.write_text(s, encoding="utf-8")
print(f"OK: заменено фрагментов: {fixed}")
