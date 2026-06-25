from pathlib import Path
import json
import pathlib
from typing import List, Dict, Any
from .models import QuestionBank, Question, Option

ROOT = Path(__file__).resolve().parent.parent
BASE = pathlib.Path(__file__).parent.parent
DATA = BASE / "data"
PACKS = DATA / "packs"
TEMPLATES = BASE / "templates"

def _read_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def _mk_option(d: Dict[str, Any]) -> Option:
    if not isinstance(d, dict):
        d = {}
    return Option(
        id=str(d.get("id", "")),
        label=d.get("label"),
        label_child=d.get("label_child"),
        label_teen=d.get("label_teen"),
        weights=d.get("weights") or {},
    )

def _mk_question(d: Dict[str, Any]) -> Question:
    if not isinstance(d, dict):
        d = {}
    opts = [_mk_option(o) for o in (d.get("options") or [])]
    return Question(
        id=str(d.get("id") or d.get("qid") or ""),
        format=d.get("format", "single"),
        text=d.get("text"),
        text_child=d.get("text_child"),
        text_teen=d.get("text_teen"),
        intro=d.get("intro"),
        intro_child=d.get("intro_child"),
        intro_teen=d.get("intro_teen"),
        options=opts,
        note=d.get("note"),
        tags=d.get("tags") or [],
    )

def load_bank(pack_name: str = "pack_classic_mods_adult_v1.json") -> QuestionBank:
    """Загружает указанный .json-файл из data/packs."""
    meta: Dict[str, Any] = {}
    features: Dict[str, Any] = {}
    questions: List[Question] = []

    pack_path = PACKS / pack_name
    print(f">>> Загрузка пака: {pack_path.name}")

    if pack_path.exists():
        obj = _read_json(pack_path)
        arr = obj.get("questions") if isinstance(obj, dict) else obj
        if isinstance(arr, list):
            for q in arr:
                questions.append(_mk_question(q))
    else:
        print("[WARN] Pack file not found!")

    questions = [q for q in questions if q.id]
    return QuestionBank(meta=meta, features=features, questions=questions)

def load_catalog() -> List[Dict[str, Any]]:
    """Каталог описаний профилей (если есть). Иначе — пусто, рендерер подставит дефолт."""
    cat = DATA / "catalog.json"
    obj = _read_json(cat)
    return obj if isinstance(obj, list) else []

def load_report_template(name: str = "report.html") -> str:
    """HTML-шаблон отчёта из templates/<name>. Если файла нет — минимальный запасной шаблон."""
    try:
        path = TEMPLATES / name
        return path.read_text(encoding="utf-8")
    except Exception:
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>\u041e\u0442\u0447\u0451\u0442</title></head>"
            "<body style='font-family:Segoe UI,Arial,sans-serif;background:#f7f8fa;margin:24px'>"
            "<h1>{{code}} — {{title}}</h1>"
            "<p>{{one_liner}}</p>"
            "<div>{{description}}</div>"
            "<h3>\u0411\u0430\u043b\u0430\u043d\u0441 \u0432\u0435\u043a\u0442\u043e\u0440\u043e\u0432</h3>{{vectors_table}}"
            "</body></html>"
        )
