from pathlib import Path
import json
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def load_catalog() -> List[Dict[str, Any]]:
    """
    Загружает каталог профилей (если есть файл data/catalog.json).
    Если файла нет или невалидный — возвращает пустой список.
    """
    cat = DATA / "catalog.json"
    if not cat.exists():
        return []
    try:
        return json.loads(cat.read_text(encoding="utf-8"))
    except Exception:
        return []
