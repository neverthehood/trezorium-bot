# hotfix: принудительный приоритет quality:rich + отладочная печать
import pathlib

p = pathlib.Path("src/main.py")
src = p.read_text(encoding="utf-8")

append_block = """

def build_route_prefer_rich(sample_size: int, chat_id: int, mode: str, style: str) -> list:
    singles_all = [q for q in bank.questions if q.format == "single" and _match_tags(q, mode, style)]
    bws_all     = [q for q in bank.questions if q.format == "rank_best_worst" and _match_tags(q, mode, style)]

    singles_rich = [q.id for q in singles_all if "quality:rich" in (q.tags or [])]
    singles_norm = [q.id for q in singles_all if "quality:rich" not in (q.tags or [])]
    bws_rich     = [q.id for q in bws_all     if "quality:rich" in (q.tags or [])]
    bws_norm     = [q.id for q in bws_all     if "quality:rich" not in (q.tags or [])]

    rnd = _rand(f"{chat_id}-{datetime.date.today().isoformat()}")
    rnd.shuffle(singles_rich); rnd.shuffle(singles_norm)
    rnd.shuffle(bws_rich);     rnd.shuffle(bws_norm)

    # rich всегда первыми; дальше — обычные (чтобы маршрут был длинным)
    singles = (singles_rich + singles_norm)[:min(sample_size, len(singles_rich)+len(singles_norm))]
    bws_ids = (bws_rich + bws_norm)

    # отладочная печать — увидишь в консоли при старте
    print(f"[router] singles rich={len(singles_rich)} norm={len(singles_norm)} | bws rich={len(bws_rich)} norm={len(bws_norm)}")

    route = []
    if not singles:
        route = bws_ids[:3]
    else:
        cut1 = max(5, len(singles)//3)
        cut2 = max(cut1 + 5, (2*len(singles))//3)
        for i, qid in enumerate(singles, 1):
            route.append(qid)
            if i == cut1 and len(bws_ids) >= 1: route.append(bws_ids[0])
            if i == cut2 and len(bws_ids) >= 2: route.append(bws_ids[1])
        if len(bws_ids) >= 3: route.append(bws_ids[2])
    return route

# используем этот маршрут вместо старого
build_route = build_route_prefer_rich
"""

if "build_route = build_route_prefer_rich" not in src:
    src += append_block
    p.write_text(src, encoding="utf-8")
    print("OK: маршрут rich добавлен и включён.")
else:
    print("Маршрут rich уже включён.")
