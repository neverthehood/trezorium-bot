# patch_store_single_and_debug.py — сохраняем выбор single в st.answers для расчётов
import re, pathlib

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8", errors="ignore").replace("\t","    ").replace("\r","")

pat = re.compile(
    r'(?ms)^@(?:dp|router)\.callback_query\(F\.data\.startswith\("ans:"\)\)\s*'
    r'\n\s*async\s+def\s+ans\s*\([^)]*\):\s*(.*?)'
    r'(?=^\s*@|^\s*async\s+def|^\s*def|^\s*class|\Z)', re.M)

m = pat.search(s)
if not m:
    raise SystemExit("Не нашёл handler ans:")

body = m.group(1)

# Уже чинили?
if 'st.answers.setdefault(qid, {})' in body and '["single"] = opt_id' in body:
    print("Уже есть сохранение single — ничего не меняю.")
else:
    # после строки с нахождением opt вставляем сохранение ответа
    body2 = re.sub(
        r'(opt\s*=\s*next\([^)]*\)\s*)\n',
        r'\1\n        st.answers.setdefault(qid, {})\n'
        r'        st.answers[qid]["single"] = opt_id\n'
        r'        st.answers[qid]["answer"] = opt_id\n',
        body, count=1)

    s = s[:m.start(1)] + body2 + s[m.end(1):]
    p.write_text(s, encoding="utf-8")
    print("OK: в ans() теперь сохраняется single/answer в st.answers.")
