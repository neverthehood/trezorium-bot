# fix_docstrings_mojibake.py — чинит "кракозябры" внутри всех тройных строк ("""...""") в src/main.py
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\","")

def looks_mojibake(txt: str) -> bool:
    return ("Р" in txt or "С" in txt) and re.search(r"[РС][\x80-\xBF]", txt) is not None

def ungarble(txt: str) -> str:
    try:
        fixed = txt.encode("latin1").decode("utf-8")
        return fixed
    except Exception:
        try:
            return txt.encode("latin1","ignore").decode("utf-8","ignore")
        except Exception:
            return txt

def repl(m: re.Match) -> str:
    body = m.group(1)
    return '"""' + (ungarble(body) if looks_mojibake(body) else body) + '"""'

s2 = re.sub(r'"""([\s\S]*?)"""', repl, s)
if s2 != s:
    p.write_text(s2, encoding="utf-8")
    print("OK: docstrings in main.py fixed.")
else:
    print("Nothing to change.")
