# fix_mojibake_packs_and_py.py — чинит "Р…/С…" в data\packs\*.json и src\*.py
import json, pathlib, re

ROOT = pathlib.Path(".")

def looks_mojibake(s: str) -> bool:
    # эвристика: много 'Р'/'С' + нет кириллицы
    return (s.count("Р") + s.count("С")) > 5 and not re.search(r"[А-Яа-яЁё]", s)

def ungarble(s: str) -> str:
    # 1) классика: utf-8 байты прочли как cp1251/latin1 -> вернуть
    try:
        t = s.encode("latin1").decode("utf-8")
        # если стало корректно и исчезли Р/С — используем
        if not looks_mojibake(t):
            return t
    except Exception:
        pass
    # 2) дубль-мойжибейк (двойное искажение) встречается редко
    try:
        t2 = s.encode("latin1").decode("utf-8").encode("latin1").decode("utf-8")
        if not looks_mojibake(t2):
            return t2
    except Exception:
        pass
    return s

def fix_in_obj(x):
    if isinstance(x, str):
        return ungarble(x) if looks_mojibake(x) else x
    if isinstance(x, list):
        return [fix_in_obj(i) for i in x]
    if isinstance(x, dict):
        return {k: fix_in_obj(v) for k,v in x.items()}
    return x

# --- JSON-паки ---
fixed = 0
for p in ROOT.glob("data/packs/*.json"):
    try:
        raw = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if not looks_mojibake(raw):
        # возможно, битые только отдельные поля — всё равно парсим
        pass
    try:
        data = json.loads(raw)
    except Exception:
        # как текст: наугад "распрямим" и попробуем ещё раз
        ung = ungarble(raw)
        data = json.loads(ung)

    new = fix_in_obj(data)
    if new != data or looks_mojibake(raw):
        p.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        print(f"FIXED JSON: {p}")
        fixed += 1

# --- PY-файлы (как плоский текст) ---
for p in [*ROOT.glob("src/*.py"), *ROOT.glob("src/**/*.py")]:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if "Р" in txt or "С" in txt:
        new = ungarble(txt)
        if new != txt:
            p.write_text(new, encoding="utf-8", newline="\n")
            print(f"FIXED PY:   {p}")
            fixed += 1

print(f"Done. Fixed items: {fixed}")
