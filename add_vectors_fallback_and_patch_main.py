# add_vectors_fallback_and_patch_main.py
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8")

# 1) импорт
if "from .vectors_fallback import compute_vectors_from_answers" not in s:
    s = s.replace("from .mods import compute_mods",
                  "from .mods import compute_mods\nfrom .vectors_fallback import compute_vectors_from_answers")

# 2) после vector_totals(st) — вставим план Б
s = re.sub(
    r"try:\s*\n\s*vectors\s*=\s*vector_totals\(st\)\s*\n\s*except Exception:\s*\n\s*vectors\s*=\s*\{\}\s*",
    r"""try:
        vectors = vector_totals(st)
    except Exception:
        vectors = {}
    # fallback: если все нули — считаем из ответов
    try:
        if not any(abs(float(v)) > 1e-9 for v in (vectors or {}).values()):
            catalog = load_catalog(getattr(st, "mode", "teen"), getattr(st, "style", "classic"))
            vectors = compute_vectors_from_answers(getattr(st, "answers", {}) or {}, catalog)
    except Exception:
        pass
""",
    s, flags=re.M
)

# 3) короткая карточка — пробрасываем vectors, чтобы был осмысленный fallback по ведущему вектору
s = s.replace("short = render_short_card(code)\n        await m.answer(short)",
              "short = render_short_card(code, vectors)\n        await m.answer(short)")

p.write_text(s, encoding="utf-8")
print("OK: main.py пропатчен — добавлен vectors_fallback и улучшен вывод краткой карточки.")
