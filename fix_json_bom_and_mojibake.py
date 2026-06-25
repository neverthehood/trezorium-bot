# fix_json_bom_and_mojibake.py — чинит BOM и "Р…/С…" в data\packs\*.json и src\*.py
import json, pathlib, re

ROOT = pathlib.Path(".")

# эвристика распознавания "моджибейка"
def looks_mojibake(s: str) -> bool:
    return ("Р" in s or "С" in s) and re.search(r"[РС][\x80-\xBF]", s) is not None

def ungarble(s: str) -> str:
    # классический случай: utf-8 было прочитано как latin-1/cp1252
    try:
        t = s.encode("latin1").decode("utf-8")
        if not looks_mojibake(t): return t
    except Exception:
        pass
    # иногда нужно два шага
    try:
        t2 = s.encode("latin1","ignore").decode("utf-8","ignore")
        if not looks_mojibake(t2): return t2
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

fixed = 0

# --- JSON-паки ---
for p in ROOT.glob("data/packs/*.json"):
    raw_bytes = p.read_bytes()  # читаем байтами
    # декодируем с utf-8-sig (убирает BOM автоматически)
    raw = raw_bytes.decode("utf-8-sig", errors="ignore")
    try:
        data = json.loads(raw)
    except Exception:
        # если структура «поплыла», попробуем распрямить текст и снова
        data = json.loads(ungarble(raw))
    new = fix_in_obj(data)
    p.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    fixed += 1
    print(f"FIXED JSON: {p}")

# --- PY-файлы ---
for p in list(ROOT.glob("src/*.py")) + list(ROOT.glob("src/**/*.py")):
    b = p.read_bytes()
    t = b.decode("utf-8-sig", errors="ignore")  # срежем BOM, если был
    new = ungarble(t) if looks_mojibake(t) else t
    if new != t or b[:3] == b"\xEF\xBB\xBF":  # был BOM или починили
        p.write_text(new, encoding="utf-8", newline="\n")
        print(f"FIXED PY:   {p}")

print("Done.")
