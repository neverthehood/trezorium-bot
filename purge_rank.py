import json, pathlib
base=pathlib.Path("data"); packs=(base/"packs")
def filt(p):
    try: d=json.loads(p.read_text(encoding="utf-8"))
    except: return
    if isinstance(d,dict) and "questions" in d:
        qs=d["questions"]; kept=[q for q in qs if isinstance(q,dict) and q.get("format")=="single"]
        if len(kept)!=len(qs):
            d["questions"]=kept; p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for f in packs.glob("*.json"): filt(f)
qb=base/"question_bank.json"
if qb.exists(): filt(qb)
print("OK: только single-вопросы остались.")
