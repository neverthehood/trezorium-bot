# debug_bank_info.py
import json, pathlib, glob
base = pathlib.Path("data/question_bank.json")
packs = list(pathlib.Path("data/packs").glob("*.json"))
def load(p): return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
q = []
if base.exists(): q += load(base)["questions"]
for p in packs:
    try:
        obj = load(p)
        q += obj.get("questions", obj)
    except: pass
print("base:", base.exists(), "packs:", len(packs))
print("total_questions:", len(q))
print("singles:", sum(1 for x in q if x.get("format")=="single"))
print("bws:", sum(1 for x in q if x.get("format")=="rank_best_worst"))
