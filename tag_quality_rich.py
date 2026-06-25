# tag_quality_rich.py — добавить тег quality:rich в 3× пакета наших историй
import json, pathlib

files = [
  "data/packs/pack_stories_handcrafted_child_v1.json",
  "data/packs/pack_stories_handcrafted_teen_v1.json",
  "data/packs/pack_stories_handcrafted_adult_v1.json",
]
for f in files:
    p = pathlib.Path(f)
    if not p.exists(): 
        print("skip (no file):", f); 
        continue
    obj = json.loads(p.read_text(encoding="utf-8"))
    arr = obj.get("questions") if isinstance(obj, dict) else obj
    ch = 0
    for q in arr or []:
        tags = q.get("tags") or []
        if "quality:rich" not in tags:
            tags.append("quality:rich")
            q["tags"] = tags
            ch += 1
    if isinstance(obj, dict):
        obj["questions"] = arr
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {f} — помечено {ch} вопросов")
