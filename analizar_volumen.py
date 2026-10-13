import csv
import bisect
from collections import defaultdict
from datetime import datetime, timedelta

UMBRAL = 0.02
HORIZONTES = [1, 24]  # horas después de la señal
TRAMOS = [
    ("menos de 1.000 USD", 0, 1000),
    ("1.000 a 10.000 USD", 1000, 10000),
    ("más de 10.000 USD", 10000, float("inf")),
]

series = defaultdict(list)
fechas = []
with open("lecturas.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        try:
            vol = float(r["volumen_24h"])
        except ValueError:
            vol = None
        fecha = datetime.fromisoformat(r["fecha"])
        fechas.append(fecha)
        series[r["id"]].append((fecha, float(r["precio"]), vol))

print(f"Desde {min(fechas):%Y-%m-%d %H:%M} hasta {max(fechas):%Y-%m-%d %H:%M}")
print(f"Lecturas distintas: {len(set(fechas))}")


def tramo(vol):
    for nombre, lo, hi in TRAMOS:
        if lo <= vol < hi:
            return nombre
    return None


stats = {}
for nombre, _, _ in TRAMOS:
    stats[nombre] = {
        "senales": 0,
        "mercados": set(),
        "res": {h: {"sigue": 0, "revierte": 0, "igual": 0} for h in HORIZONTES},
    }

for id_, pts in series.items():
    pts.sort(key=lambda p: p[0])
    tiempos = [p[0] for p in pts]
    for i in range(1, len(pts)):
        dif = pts[i][1] - pts[i - 1][1]
        if abs(dif) < UMBRAL or pts[i][2] is None:
            continue
        t = tramo(pts[i][2])
        if t is None:
            continue
        s = stats[t]
        s["senales"] += 1
        s["mercados"].add(id_)
        for h in HORIZONTES:
            j = bisect.bisect_left(tiempos, pts[i][0] + timedelta(hours=h))
            if j >= len(pts):
                continue
            despues = pts[j][1] - pts[i][1]
            if despues == 0:
                s["res"][h]["igual"] += 1
            elif (despues > 0) == (dif > 0):
                s["res"][h]["sigue"] += 1
            else:
                s["res"][h]["revierte"] += 1

for nombre, _, _ in TRAMOS:
    s = stats[nombre]
    print(f"\n=== Volumen 24h: {nombre} ===")
    print(f"Señales: {s['senales']} en {len(s['mercados'])} mercados distintos")
    for h in HORIZONTES:
        r = s["res"][h]
        total = sum(r.values())
        if total:
            print(f"  A {h} h ({total} casos): sigue {r['sigue']/total:.0%}, "
                  f"revierte {r['revierte']/total:.0%}, igual {r['igual']/total:.0%}")