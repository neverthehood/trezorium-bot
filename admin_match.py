# admin_match.py Р Р†Р вЂљРІР‚Сњ Р В РЎвЂўР РЋРІР‚С›Р РЋРІР‚С›Р В Р’В»Р В Р’В°Р В РІвЂћвЂ“Р В Р вЂ¦-Р В РЎвЂ”Р В РЎвЂўР В РўвЂР В Р’В±Р В РЎвЂўР РЋР вЂљ Р В РЎвЂ”Р В Р’В°Р РЋР вЂљ Р В РЎвЂ”Р В РЎвЂў Р В РўвЂР В Р’В°Р В Р вЂ¦Р В Р вЂ¦Р РЋРІР‚в„–Р В РЎВ results.jsonl
# Р В РЎСџР РЋР вЂљР В РЎвЂР В РЎВР В Р’ВµР РЋР вЂљР РЋРІР‚в„–:
#   python admin_match.py --for @username --top 10
#   python admin_match.py --for-id 123456789 --aud teen --top 5
import json, pathlib, math, argparse, re
P = pathlib.Path("data/results.jsonl")

def load_latest_by_user():
    by_user = {}
    if not P.exists(): return {}
    with open(P, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except:
                continue
            uid = r.get("chat_id")
            ts = r.get("ts", 0)
            prev = by_user.get(uid)
            if not prev or ts > prev.get("ts", 0):
                by_user[uid] = r
    return by_user

def vec4(d):
    # Р В РЎвЂР РЋР С“Р В РЎвЂ”Р В РЎвЂўР В Р’В»Р РЋР Р‰Р В Р’В·Р РЋРЎвЂњР В Р’ВµР В РЎВ G,S,T,K; Р В РЎвЂўР РЋРІР‚С™Р РЋР С“Р РЋРЎвЂњР РЋРІР‚С™Р РЋР С“Р РЋРІР‚С™Р В Р вЂ Р В РЎвЂР В Р’Вµ Р Р†Р вЂљРІР‚Сњ 0
    return [float(d.get("G",0)), float(d.get("S",0)), float(d.get("T",0)), float(d.get("K",0))]

def cosine(a,b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
    if na==0 or nb==0: return 0.0
    return dot/(na*nb)

def role_vector(v):  # GР Р†РІвЂљВ¬РІР‚в„ўS, KР Р†РІвЂљВ¬РІР‚в„ўT
    G,S,T,K = v
    return [G - S, K - T]

def score_pair(v1, v2, alpha=0.6, beta=0.4):
    # Р В РЎвЂ”Р В РЎвЂўР РЋРІР‚В¦Р В РЎвЂўР В Р’В¶Р В Р’ВµР РЋР С“Р РЋРІР‚С™Р РЋР Р‰ Р РЋР вЂљР В РЎвЂР РЋРІР‚С™Р В РЎВР В РЎвЂўР В Р вЂ  (Р В РЎвЂќР В РЎвЂўР РЋР С“Р В РЎвЂР В Р вЂ¦Р РЋРЎвЂњР РЋР С“ Р В РЎвЂ”Р В РЎвЂў 4 Р В РЎвЂўР РЋР С“Р РЋР РЏР В РЎВ) Р Р†РІР‚В РІР‚в„ў [0..1]
    sim = (cosine(v1, v2) + 1)/2
    # Р В РўвЂР В РЎвЂўР В РЎвЂ”Р В РЎвЂўР В Р’В»Р В Р вЂ¦Р В Р’ВµР В Р вЂ¦Р В РЎвЂР В Р’Вµ Р РЋР вЂљР В РЎвЂўР В Р’В»Р В Р’ВµР В РІвЂћвЂ“: Р РЋРІР‚В¦Р В РЎвЂўР РЋРІР‚РЋР В Р’ВµР РЋРІР‚С™Р РЋР С“Р РЋР РЏ Р вЂ™Р’В«Р В Р вЂ¦Р В Р’В°Р В РЎвЂ”Р РЋР вЂљР В РЎвЂўР РЋРІР‚С™Р В РЎвЂР В Р вЂ Р вЂ™Р’В» Р В РЎвЂ”Р В РЎвЂў (GР Р†РІвЂљВ¬РІР‚в„ўS, KР Р†РІвЂљВ¬РІР‚в„ўT)
    r1, r2 = role_vector(v1), role_vector(v2)
    comp = (cosine(r1, [-x for x in r2]) + 1)/2
    return alpha*sim + beta*comp, sim, comp

def select_pool(by_user, audience=None, exclude_id=None):
    out=[]
    for uid, r in by_user.items():
        if exclude_id and uid == exclude_id: continue
        if audience and r.get("audience_mode") != audience: continue
        v = vec4(r.get("vectors", {}))
        out.append((uid, r.get("username"), r.get("audience_mode"), r.get("gender","unknown"), v, r))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--for", dest="for_user", help="@username Р РЋРІР‚В Р В Р’ВµР В Р’В»Р В Р’ВµР В Р вЂ Р В РЎвЂўР В РЎвЂ“Р В РЎвЂў Р В РЎвЂ”Р В РЎвЂўР В Р’В»Р РЋР Р‰Р В Р’В·Р В РЎвЂўР В Р вЂ Р В Р’В°Р РЋРІР‚С™Р В Р’ВµР В Р’В»Р РЋР РЏ")
    ap.add_argument("--for-id", dest="for_id", type=int, help="chat_id Р РЋРІР‚В Р В Р’ВµР В Р’В»Р В Р’ВµР В Р вЂ Р В РЎвЂўР В РЎвЂ“Р В РЎвЂў Р В РЎвЂ”Р В РЎвЂўР В Р’В»Р РЋР Р‰Р В Р’В·Р В РЎвЂўР В Р вЂ Р В Р’В°Р РЋРІР‚С™Р В Р’ВµР В Р’В»Р РЋР РЏ")
    ap.add_argument("--aud", dest="aud", choices=["child","teen","adult"], help="Р РЋРІР‚С›Р В РЎвЂР В Р’В»Р РЋР Р‰Р РЋРІР‚С™Р РЋР вЂљ Р В Р’В°Р РЋРЎвЂњР В РўвЂР В РЎвЂР РЋРІР‚С™Р В РЎвЂўР РЋР вЂљР В РЎвЂР В РЎвЂ")
    ap.add_argument("--top", dest="top", type=int, default=10, help="Р РЋР С“Р В РЎвЂќР В РЎвЂўР В Р’В»Р РЋР Р‰Р В РЎвЂќР В РЎвЂў Р В РЎвЂ”Р В РЎвЂўР В РЎвЂќР В Р’В°Р В Р’В·Р В Р’В°Р РЋРІР‚С™Р РЋР Р‰")
    args = ap.parse_args()

    by_user = load_latest_by_user()
    target = None
    if args.for_id:
        target = by_user.get(args.for_id)
    elif args.for_user:
        uname = args.for_user.lstrip("@").lower()
        for r in by_user.values():
            if (r.get("username") or "").lower() == uname:
                target = r; break
    if not target:
        print("Р В Р’В¦Р В Р’ВµР В Р’В»Р В Р’ВµР В Р вЂ Р В РЎвЂўР В РІвЂћвЂ“ Р В РЎвЂ”Р В РЎвЂўР В Р’В»Р РЋР Р‰Р В Р’В·Р В РЎвЂўР В Р вЂ Р В Р’В°Р РЋРІР‚С™Р В Р’ВµР В Р’В»Р РЋР Р‰ Р В Р вЂ¦Р В Р’Вµ Р В Р вЂ¦Р В Р’В°Р В РІвЂћвЂ“Р В РўвЂР В Р’ВµР В Р вЂ¦.")
        return

    tv = vec4(target.get("vectors", {}))
    pool = select_pool(by_user, audience=args.aud or target.get("audience_mode"), exclude_id=target.get("chat_id"))

    scored=[]
    for uid, uname, aud, gender, v, rec in pool:
        s, sim, comp = score_pair(tv, v)
        scored.append((s, sim, comp, uid, uname, aud, gender))
    scored.sort(key=lambda x: x[0], reverse=True)

    print(f"Р В Р’В¦Р В Р’ВµР В Р’В»Р РЋР Р‰: id={target.get('chat_id')} @{target.get('username')} aud={target.get('audience_mode')} gender={target.get('gender')}")
    print("Р В РЎС›Р В РЎвЂўР В РЎвЂ” Р РЋР С“Р В РЎвЂўР В Р вЂ Р В РЎвЂ”Р В Р’В°Р В РўвЂР В Р’ВµР В Р вЂ¦Р В РЎвЂР В РІвЂћвЂ“:")
    for s, sim, comp, uid, uname, aud, gender in scored[:args.top]:
        print(f"{s:0.3f}  (sim={sim:0.3f}, comp={comp:0.3f})  id={uid}  @{uname}  aud={aud}  gender={gender}")

if __name__=="__main__":
    main()
