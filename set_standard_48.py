# set_standard_48.py
from pathlib import Path, re
p = Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore")
import re
s = re.sub(r'sample_map\s*=\s*\{[^}]*\}',
           'sample_map = {"express": 24, "standard": 48, "deep": 72}',
           s, count=1)
p.write_text(s, encoding="utf-8")
print("OK: sample_map set to 24/48/72")
