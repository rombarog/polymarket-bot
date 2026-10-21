import csv
import json
from collections import defaultdict
from datetime import datetime
from statistics import median

UMBRAL = 0.02

libro = {}
with open("libro.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        try:
            libro[(r["fecha"], r["id"])] = (float(r["mejor_compra"]), float(r["mejor_venta"]))
        except ValueError:
            pass

with open("mercados.json", encoding="utf-8") as f:
    nombres = json.load(f)

series = defaultdict(list)
with open("lecturas.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        c = (r["fecha"], r["id"])
        if c in libro:
            bid, ask = libro[c]
            series[r["id"]].append((datetime.fromisoformat(r["fecha"]), float(r["precio"]), bid, ask))

senales = []
for id_, pts in series.items():
    pts.sort(key=lambda p: p[0])
    for i in range(1, len(pts)):
        _, p1, bid, ask = pts[i]
        p0 = pts[i - 1][1]
        if abs(p1 - p0) >= UMBRAL and 0 < bid <= ask < 1:
            senales.append((id_, p0, p1, bid, ask))

print(f"Señales con libro válido: {len(senales)}")
sp = [(a - b) * 100 for _, _, _, b, a in senales]
print(f"Spread en el momento de la señal (centavos): mediana {median(sp):.1f}")
print(f"Señales con spread mayor a 10 centavos: {sum(1 for s in sp if s > 10) / len(sp):.0%}")
fuera = sum(1 for _, _, p1, b, a in senales if not (b <= p1 <= a))
print(f"Señales donde el precio guardado queda fuera de compra/venta: {fuera / len(senales):.0%}")

print("\nEjemplos (precio antes -> ahora | compra / venta | mercado):")
for id_, p0, p1, b, a in senales[:10]:
    print(f"{p0:.3f} -> {p1:.3f} | {b:.3f} / {a:.3f} | {nombres.get(id_, id_)[:50]}")