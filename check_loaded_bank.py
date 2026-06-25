from src.question_loader import load_bank
b = load_bank()
singles = sum(1 for q in b.questions if q.format=="single")
bws = sum(1 for q in b.questions if q.format=="rank_best_worst")
by_child = sum(1 for q in b.questions if "aud:child" in (q.tags or []))
by_teen  = sum(1 for q in b.questions if "aud:teen"  in (q.tags or []))
by_adult = sum(1 for q in b.questions if "aud:adult" in (q.tags or []))
print("TOTAL:", len(b.questions), "singles:", singles, "bws:", bws)
print("aud child/teen/adult:", by_child, by_teen, by_adult)
