# fix_vectors_block_indent.py — выравнивает отступы блока с fallback-векторами
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8")

lines = s.splitlines(True)

# найти строку с нашим маркером
marker = "# fallback: если все нули — считаем из ответов"
try:
    midx = next(i for i,l in enumerate(lines) if marker in l)
except StopIteration:
    print("Маркер не найден — ничего не меняю.")
    raise SystemExit(0)

# найти начало блока (ближайший «try:» выше)
start = midx
while start >= 0 and lines[start].strip() != "try:":
    start -= 1
if start < 0:
    print("Стартовый try: не найден — выхожу.")
    raise SystemExit(1)

# найти конец блока (первый «pass» ниже после «except Exception:»)
end = midx
seen_except = False
while end < len(lines):
    t = lines[end].strip()
    if t.startswith("except Exception"):
        seen_except = True
    if seen_except and t == "pass":
        break
    end += 1
if end >= len(lines):
    print("Конец блока не найден — выхожу.")
    raise SystemExit(1)

indent = lines[start][:len(lines[start]) - len(lines[start].lstrip())]

block = (
    f"{indent}try:\n"
    f"{indent}    vectors = vector_totals(st)\n"
    f"{indent}except Exception:\n"
    f"{indent}    vectors = {{}}\n"
    f"{indent}{marker}\n"
    f"{indent}try:\n"
    f"{indent}    if not any(abs(float(v)) > 1e-9 for v in (vectors or {{}}).values()):\n"
    f"{indent}        catalog = load_catalog(getattr(st, \"mode\", \"teen\"), getattr(st, \"style\", \"classic\"))\n"
    f"{indent}        vectors = compute_vectors_from_answers(getattr(st, \"answers\", {{}}) or {{}}, catalog)\n"
    f"{indent}except Exception:\n"
    f"{indent}    pass\n"
)

new_s = "".join(lines[:start]) + block + "".join(lines[end+1:])
p.write_text(new_s, encoding="utf-8")
print("OK: блок расчёта vectors выровнен по отступам.")
