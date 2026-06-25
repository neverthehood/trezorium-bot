# hotfix_root_paths.py  привязывает пути к корню проекта
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent

files = [
    "src/main.py",
    "src/result_renderer.py",
    "src/question_loader.py",
    "src/config.py",
    "runner_poll.py",
]

def ensure_root_header(txt: str) -> str:
    if "ROOT = Path(__file__).resolve().parent.parent" in txt:
        return txt
    # добавим импорт Path и ROOT, если их нет
    if "from pathlib import Path" not in txt:
        txt = "from pathlib import Path\n" + txt
    # после первых импортов  вставим ROOT
    lines = txt.splitlines(True)
    ins = 0
    for i, ln in enumerate(lines):
        if ln.startswith("from ") or ln.startswith("import "):
            ins = i + 1
    lines.insert(ins, "ROOT = Path(__file__).resolve().parent.parent\n")
    return "".join(lines)

def patch_data_paths(txt: str) -> str:
    # Path("data/...") -> ROOT / "data/..."
    txt = re.sub(r'\bPath\(\s*[\'"]data/([^\'"]+)[\'"]\s*\)', r'ROOT / "data/\1"', txt)
    # pathlib.Path("data/...") -> ROOT / "data/..."
    txt = re.sub(r'\bpathlib\.Path\(\s*[\'"]data/([^\'"]+)[\'"]\s*\)', r'ROOT / "data/\1"', txt)
    # open("data/...") -> open(str(ROOT / "data/..."), encoding="utf-8-sig") (если encoding не указан)
    txt = re.sub(
        r'open\(\s*[\'"]data/([^\'"]+)[\'"]\s*\)',
        r'open(str(ROOT / "data/\1"), encoding="utf-8-sig")',
        txt
    )
    # reports_dir = Path("data/reports") -> reports_dir = ROOT / "data" / "reports"
    txt = re.sub(
        r'reports_dir\s*=\s*(?:pathlib\.)?Path\(\s*[\'"]data/reports[\'"]\s*\)',
        r'reports_dir = ROOT / "data" / "reports"',
        txt
    )
    return txt

def patch_runner_cwd(txt: str, filename: str) -> str:
    if filename != "runner_poll.py":
        return txt
    # добавим chdir(ROOT) в раннер
    if "os.chdir(ROOT)" in txt:
        return txt
    if "import os" not in txt:
        txt = txt.replace("import asyncio", "import asyncio, os")
    # найдём место после определения ROOT
    if "ROOT = Path(__file__).resolve().parent" in txt:
        return txt  # уже ок
    if "from pathlib import Path" not in txt:
        txt = "from pathlib import Path\n" + txt
    lines = txt.splitlines(True)
    # вставим ROOT= и chdir в начало файла (после импортов)
    ins = 0
    for i, ln in enumerate(lines):
        if ln.startswith("from ") or ln.startswith("import "):
            ins = i + 1
    lines.insert(ins, "ROOT = Path(__file__).resolve().parent\nos.chdir(ROOT)\n")
    return "".join(lines)

for rel in files:
    p = ROOT / rel
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8", errors="ignore")
    orig = txt
    txt = ensure_root_header(txt)
    txt = patch_data_paths(txt)
    txt = patch_runner_cwd(txt, rel)
    if txt != orig:
        p.write_text(txt, encoding="utf-8")
        print(f"PATCHED: {rel}")

print("Done.")
