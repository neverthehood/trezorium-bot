# hotfix_main_use_mods.py — подключаем mods в finish_and_report
import pathlib, re
p=pathlib.Path("src/main.py"); s=p.read_text(encoding="utf-8")
if "from .mods import compute_mods" not in s:
    s=s.replace("from .engine import apply_weights, pick_result, vector_totals",
                "from .engine import apply_weights, pick_result, vector_totals\nfrom .mods import compute_mods")
s=re.sub(r"render_html_report\((\s*code,\s*vectors,\s*features,\s*neighbors\s*)\)",
         r"render_html_report(\1, mods)", s)
# перед вызовом render_html_report добавим расчёт mods
s=re.sub(r"(vectors\s*=\s*vector_totals\(.*?\)\s*)\n", r"\1\n    mods = compute_mods(st.answers, bank)\n", s, flags=re.DOTALL)
p.write_text(s,encoding="utf-8"); print("OK: main.py теперь считает mods и передаёт в отчёт.")
