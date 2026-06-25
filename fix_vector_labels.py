# fix_vector_labels.py
from pathlib import Path, re
p = Path("src/result_renderer.py")
s = p.read_text(encoding="utf-8", errors="ignore")
s = s.replace("Связи", "Сердце").replace("Практика", "Руки")
# На случай словаря вида {"G":"Голова","S":"Связи","T":"Практика","K":"Креатив"}
import re
s = re.sub(r'("S"\s*:\s*")([^"]*)"', r'\1Сердце"', s)
s = re.sub(r'("T"\s*:\s*")([^"]*)"', r'\1Руки"', s)
p.write_text(s, encoding="utf-8")
print("OK: labels => Голова, Сердце, Руки, Креатив")
