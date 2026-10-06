import csv
from collections import defaultdict, Counter
from datetime import datetime

UMBRAL = 0.02

series = defaultdict(list)
nombres = {}
with open("historial.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        series[r["id"]].append((datetime.fromisoformat(r["fecha"]), float(r["precio"])))
        nombres[r["id"]] = r["pregunta"]

cuenta = Counter()
for id_, pts in series.items():
    pts.sort()
    for i in range(1, len(pts)):
        if abs(pts[i][1] - pts[i - 1][1]) >= UMBRAL:
            cuenta[id_] += 1

total = sum(cuenta.values())
print(f"Total de señales: {total}")
for id_, n in cuenta.most_common(10):
    print(f"{n} ({n/total:.0%}) | {nombres[id_]}")