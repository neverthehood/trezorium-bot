# fix_mojibake_everywhere.py — чинит "Р…" / "С…" во всех .py/.json
import re, pathlib

ROOT = pathlib.Path(".")
FILES = [*ROOT.rglob("src/**/*.py"), *ROOT.rglob("data/**/*.json"), *ROOT.glob("*.py")]

def looks_mojibake(s: str) -> bool:
    return (s.count("Р") + s.count("С")) > 10 and re.search(r"[РС][\x80-\xBF]", s)

def ungarble(s: str) -> str:
    # UTF-8 прочитали как cp1251/cp1252 → вернуть назад
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        try:
            return s.encode("cp1252", "ignore").decode("utf-8", "ignore")
        except Exception:
            return s

fixed = 0
for p in FILES:
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if looks_mojibake(text):
        new = ungarble(text)
        if new != text and not looks_mojibake(new):
            p.write_text(new, encoding="utf-8", newline="\n")
            print(f"FIXED: {p}")
            fixed += 1
print(f"Done. Fixed files: {fixed}")
