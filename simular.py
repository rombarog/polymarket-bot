import csv
import bisect
from collections import defaultdict
from datetime import datetime, timedelta

UMBRAL = 0.02
APUESTA = 20          # USD por señal
PRECIO_MIN = 0.05     # ignorar entradas muy baratas o muy caras
PRECIO_MAX = 0.95
HORIZONTES = [1, 24]  # horas hasta cerrar la operación
COSTOS = [0, 0.01, 0.02, 0.04]  # spread asumido, por lado

series = defaultdict(list)
with open("lecturas.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        series[r["id"]].append((datetime.fromisoformat(r["fecha"]), float(r["precio"])))

operaciones = defaultdict(list)  # (estrategia, horas) -> [(entrada, salida)]

for id_, pts in series.items():
    pts.sort(key=lambda p: p[0])
    tiempos = [p[0] for p in pts]
    for i in range(1, len(pts)):
        p0, p1 = pts[i - 1][1], pts[i][1]
        dif = p1 - p0
        if abs(dif) < UMBRAL:
            continue
        for h in HORIZONTES:
            j = bisect.bisect_left(tiempos, pts[i][0] + timedelta(hours=h))
            if j >= len(pts):
                continue
            p2 = pts[j][1]
            if dif > 0:
                seguir = (p1, p2)            # comprar Sí
                revertir = (1 - p1, 1 - p2)  # comprar No
            else:
                seguir = (1 - p1, 1 - p2)    # comprar No
                revertir = (p1, p2)          # comprar Sí
            operaciones[("revertir", h)].append(revertir)
            operaciones[("seguir", h)].append(seguir)


def resultado(ops, costo):
    total, n, ganadas = 0.0, 0, 0
    for entrada, salida in ops:
        if not (PRECIO_MIN <= entrada <= PRECIO_MAX):
            continue
        compra = entrada + costo
        venta = salida - costo
        pnl = (APUESTA / compra) * venta - APUESTA
        total += pnl
        n += 1
        if pnl > 0:
            ganadas += 1
    return n, total, ganadas


for h in HORIZONTES:
    for estrategia in ["revertir", "seguir"]:
        print(f"\n=== {estrategia.upper()} | cerrar a las {h} h ===")
        for costo in COSTOS:
            n, total, ganadas = resultado(operaciones[(estrategia, h)], costo)
            if n == 0:
                continue
            print(f"  spread {costo*100:.0f} cent/lado: {n} operaciones, "
                  f"ganó {ganadas/n:.0%}, total {total:+.0f} USD "
                  f"({total/n:+.2f} por operación)")