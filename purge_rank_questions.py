# purge_rank_questions.py — оставляет только истории (format == "single")
import json, pathlib, sys

changed_files = []
removed_total = 0
kept_total = 0

def filter_file(path: pathlib.Path):
    global removed_total, kept_total
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return
    if isinstance(data, dict) and "questions" in data:
        qs = data.get("questions") or []
        kept = [q for q in qs if (isinstance(q, dict) and q.get("format") == "single")]
        removed = len(qs) - len(kept)
        if removed > 0:
            data["questions"] = kept
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            changed_files.append((str(path), removed))
            removed_total += removed
            kept_total += len(kept)
        else:
            kept_total += len(kept)

base = pathlib.Path("data")
packs = base / "packs"
for p in packs.glob("*.json"):
    filter_file(p)

qb = base / "question_bank.json"
if qb.exists():
    filter_file(qb)

print("OK: очищено.")
for name, rm in changed_files:
    print(f"  {name}: удалено не-single вопросов = {rm}")
print(f"Итог: удалено {removed_total}, осталось single = {kept_total}")
