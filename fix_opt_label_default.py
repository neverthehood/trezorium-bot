# fix_opt_label_default.py — меняет битую строку на "Вариант" в opt_label()
from pathlib import Path
p = Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\","")
s_new = s.replace("Р’Р°СЂРёР°РЅС‚", "Вариант")
if s_new != s:
    p.write_text(s_new, encoding="utf-8")
    print("OK: заменил битую строку на 'Вариант'.")
else:
    print("Изменений не требовалось (ничего не нашёл).")
