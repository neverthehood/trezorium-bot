# fix_main_leftover_comments.py — чинит битые комментарии в src/main.py
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\","")

def looks_mojibake_line(line: str) -> bool:
    return line.lstrip().startswith("#") and ("Р" in line or "С" in line)

def ungarble(txt: str) -> str:
    try:
        t = txt.encode("latin1").decode("utf-8")
        return t
    except Exception:
        try:
            return txt.encode("latin1","ignore").decode("utf-8","ignore")
        except Exception:
            return txt

fixed_lines = []
out = []
for line in s.splitlines(True):
    if looks_mojibake_line(line):
        new = ungarble(line)
        if new != line:
            fixed_lines.append((line.rstrip("\n"), new.rstrip("\n")))
            line = new
    out.append(line)

p.write_text("".join(out), encoding="utf-8")
print("Fixed lines:")
for old, new in fixed_lines:
    print("  -", old)
    print("  +", new)
print(f"Done. Patched {len(fixed_lines)} comment line(s).")
