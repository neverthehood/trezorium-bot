# normalize_main_indent.py — нормализует src/main.py и выравнивает декораторы/функции
import re, pathlib, shutil

p = pathlib.Path("src/main.py")
txt = p.read_text(encoding="utf-8", errors="ignore")

# 1) Нормализация невидимых символов и табов
txt = txt.replace("\","").replace("\ "," ")
txt = txt.replace("\r","")
txt = txt.replace("\t","    ")

lines = txt.splitlines(True)

new_lines = []
prev_sig = ""   # предыдущая "значимая" строка (без пустых)
last_was_decorator = False

for i, line in enumerate(lines):
    raw = line

    # Если это строка-декоратор — сносим все ведущие пробелы
    if re.match(r'^\s*@(?:dp|router)\.', line):
        line = line.lstrip()
        last_was_decorator = True
    # Если это заголовок функции и до этого был декоратор — тоже без отступа
    elif re.match(r'^\s*(?:async\s+def|def)\s+', line) and last_was_decorator:
        line = line.lstrip()
        last_was_decorator = False
    else:
        # Сброс флага, если между декоратором и def вклинилось что-то ещё
        if line.strip() != "" and not re.match(r'^\s*(?:async\s+def|def)\s+', line):
            last_was_decorator = False

    new_lines.append(line)
    if line.strip():
        prev_sig = line

# 2) На всякий — если прямо перед set_aud «висит» заголовок без тела, вставим pass
txt2 = "".join(new_lines)
ls = txt2.splitlines(True)
idx = None
for i, ln in enumerate(ls):
    if re.match(r'^\s*async\s+def\s+set_aud\s*\(', ln):
        idx = i
        break
if idx is not None:
    j = idx - 1
    while j >= 0 and ls[j].strip() == "":
        j -= 1
    if j >= 0 and ls[j].rstrip().endswith(":"):
        # Проверим, есть ли тело между заголовком и set_aud
        head_indent = len(ls[j]) - len(ls[j].lstrip(" "))
        body_found = False
        for k in range(j+1, idx):
            if ls[k].strip() != "":
                lead = len(ls[k]) - len(ls[k].lstrip(" "))
                if lead > head_indent:
                    body_found = True
                    break
        if not body_found:
            ls.insert(idx, " "*(head_indent+4) + "pass\n")
            txt2 = "".join(ls)

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(txt2, encoding="utf-8")
print("OK: main.py нормализован; декораторы и def выровнены; резервная копия: src/main.py.bak")
