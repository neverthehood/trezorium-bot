# hotfix_route_single_only.py — маршрут "только single stories"
import pathlib, re

p = pathlib.Path("src/main.py")
s = p.read_text(encoding="utf-8")

def ensure(text, needle, before=None):
    if needle not in text and before and before in text:
        return text.replace(before, needle + "\n" + before)
    return text

# На всякий: оставляем фильтр по стилю и аудитории
if "def _match_tags" not in s:
    s = s.replace("def kb_single", "def _match_tags(q, mode, style):\n    t=set(getattr(q,'tags',[]) or [])\n    return (f'aud:{mode}' in t) and (f'style:{style}' in t)\n\n\ndef kb_single", 1)

# Полностью переписываем build_route → только single и только style:story
pat = r"def build_route\(.*?\):.*?return route"
s = re.sub(
    pat,
    r"""def build_route(sample_size: int, chat_id: int, mode: str, style: str) -> list:
    # берём только single и только по стилю/аудитории
    singles = [q.id for q in bank.questions if q.format=='single' and _match_tags(q, mode, style)]
    rnd = _rand(f"{chat_id}-{datetime.date.today().isoformat()}")
    rnd.shuffle(singles)
    return singles[:min(sample_size, len(singles))]
""",
    s, flags=re.DOTALL)

p.write_text(s, encoding="utf-8")
print("OK: маршрут теперь только stories (single), без ранжирований.")
