import csv
import bisect
from collections import defaultdict
from datetime import datetime, timedelta

UMBRAL = 0.02
HORIZONTES = [1, 24]  # horas después de la señal

series = defaultdict(list)
with open("historial.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        series[r["id"]].append((datetime.fromisoformat(r["fecha"]), float(r["precio"])))

resultados = {h: {"sigue": 0, "revierte": 0, "igual": 0} for h in HORIZONTES}
senales = 0
mercados_con_senal = set()

for id_, pts in series.items():
    pts.sort()
    tiempos = [p[0] for p in pts]
    for i in range(1, len(pts)):
        dif = pts[i][1] - pts[i - 1][1]
        if abs(dif) < UMBRAL:
            continue
        senales += 1
        mercados_con_senal.add(id_)
        for h in HORIZONTES:
            j = bisect.bisect_left(tiempos, pts[i][0] + timedelta(hours=h))
            if j >= len(pts):
                continue
            despues = pts[j][1] - pts[i][1]
            if despues == 0:
                resultados[h]["igual"] += 1
            elif (despues > 0) == (dif > 0):
                resultados[h]["sigue"] += 1
            else:
                resultados[h]["revierte"] += 1

print(f"Señales de {UMBRAL} o más: {senales}")
print(f"Mercados distintos con señal: {len(mercados_con_senal)}")
for h in HORIZONTES:
    r = resultados[h]
    total = sum(r.values())
    print(f"\nA {h} h de la señal ({total} casos medibles):")
    if total:
        print(f"  Siguió en la misma dirección: {r['sigue']} ({r['sigue']/total:.0%})")
        print(f"  Revirtió: {r['revierte']} ({r['revierte']/total:.0%})")
        print(f"  Quedó igual: {r['igual']} ({r['igual']/total:.0%})")