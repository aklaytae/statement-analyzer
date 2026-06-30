
from collections import defaultdict

def summarize_daily(transactions):
    summary = defaultdict(lambda: {"income": 0, "expense": 0})

    for t in transactions:
        date = t["date"].date()

        summary[date]["income"] += t["income"]
        summary[date]["expense"] += t["expense"]

    result = []

    for date, val in summary.items():
        net = val["income"] - val["expense"]

        result.append({
            "date": str(date),
            "income": round(val["income"], 2),
            "expense": round(val["expense"], 2),
            "net": round(net, 2)
        })

    return sorted(result, key=lambda x: x["date"])