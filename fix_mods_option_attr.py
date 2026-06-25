# fix_mods_option_attr.py — делает mods.py совместимым с dict и pydantic-моделями Option
import re, pathlib, shutil

p = pathlib.Path("src/mods.py")
s = p.read_text(encoding="utf-8", errors="ignore")

# 1) Аккуратно добавим хелперы наверху файла (если их ещё нет)
helpers = """
# --- helpers: support dict and pydantic/BaseModel objects uniformly ---
def getv(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def weights_of(obj):
    w = getv(obj, "weights", {})
    return w if isinstance(w, dict) else {}
# --- end helpers ---
"""

if "def getv(obj, key" not in s:
    s = helpers.lstrip() + "\n" + s

# 2) Заменим обращения .get("...") на getv(..., "...") (чтобы работало и для объектов)
s = re.sub(r'(\b\w+)\.get\("([^"]+)"\s*\)', r'getv(\1, "\2")', s)
s = re.sub(r'(\b\w+)\.get\("([^"]+)"\s*,\s*([^)]+)\)', r'getv(\1, "\2", \3)', s)

# 3) Где берём weights — используем weights_of(...)
s = re.sub(r'getv\(([^,]+),\s*"weights"\)', r'weights_of(\1)', s)
s = re.sub(r'getv\(([^,]+),\s*"weights"\s*,\s*[^)]+\)', r'weights_of(\1)', s)

# Бэкап и запись
shutil.copyfile(p, p.with_suffix(".py.bak"))
p.write_text(s, encoding="utf-8")
print("OK: mods.py теперь читает id/weights и из dict, и из Option.")
