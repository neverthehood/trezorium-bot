# fix_insert_pass_before_set_aud.py — вставляет pass перед set_aud, если над ним "висящий" заголовок
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# Нормализация
s = s.replace("\","").replace("\ "," ").replace("\r","")

lines = s.splitlines(True)

# Найдём строку с set_aud
idx = None
for i, line in enumerate(lines):
    if re.match(r'^\s*async\s+def\s+set_aud\s*\(', line):
        idx = i
        break

if idx is None:
    raise SystemExit("Не нашёл set_aud — ничего не менял.")

# Ищем последнюю непустую строку выше
j = idx - 1
while j >= 0 and lines[j].strip() == "":
    j -= 1

need_insert = False
indent = ""
if j >= 0:
    prev = lines[j].rstrip("\n")
    # Если предыдущая непустая строка оканчивается ":" — это заголовок блока.
    if prev.rstrip().endswith(":"):
        # Проверим, есть ли между j и idx хоть одна непустая С ОТСТУПОМ (то есть тело блока)
        body_found = False
        for k in range(j+1, idx):
            if lines[k].strip() != "":
                # есть непробельная строка; считаем тело найденным, если она строго более вдавлена чем заголовок
                lead_prev = len(prev) - len(prev.lstrip(" "))
                lead_k    = len(lines[k]) - len(lines[k].lstrip(" "))
                if lead_k > lead_prev:
                    body_found = True
                    break
        if not body_found:
            need_insert = True
            lead_prev = len(prev) - len(prev.lstrip(" "))
            indent = " " * (lead_prev + 4)

if need_insert:
    lines.insert(idx, indent + "pass\n")
    s2 = "".join(lines)
    p.write_text(s2, encoding="utf-8")
    print("OK: вставил pass перед set_aud.")
else:
    print("OK: тело перед set_aud найдено — ничего не менял.")
