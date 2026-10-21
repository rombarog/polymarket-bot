import csv
import bisect
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median

UMBRAL = 0.02
APUESTA = 20
PMIN, PMAX = 0.05, 0.95
HORIZONTES = [1, 24]

libro = {}
with open("libro.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        try:
            libro[(r["fecha"], r["id"])] = (float(r["mejor_compra"]), float(r["mejor_venta"]))
        except ValueError:
            pass

series = defaultdict(list)
with open("lecturas.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        clave = (r["fecha"], r["id"])
        if clave not in libro:
            continue
        try:
            vol = float(r["volumen_24h"])
        except ValueError:
            vol = None
        bid, ask = libro[clave]
        series[r["id"]].append((datetime.fromisoformat(r["fecha"]), float(r["precio"]), bid, ask, vol))


def libro_valido(bid, ask):
    return 0 < bid <= ask < 1


def tramo(vol):
    return "menos de 1.000 USD" if (vol is not None and vol < 1000) else "1.000 USD o más"


# 1) Spread típico por nivel de volumen (en centavos)
spreads = defaultdict(list)
for pts in series.values():
    for _, _, bid, ask, vol in pts:
        if libro_valido(bid, ask):
            spreads[tramo(vol)].append((ask - bid) * 100)
print("Spread típico (compra-venta, en centavos):")
for t, v in spreads.items():
    print(f"  {t}: mediana {median(v):.1f} | {len(v)} lecturas")

# 2) Simulación con precios reales: se compra al 'ask' y se vende al 'bid'
res = defaultdict(list)
for pts in series.values():
    pts.sort(key=lambda p: p[0])
    tiempos = [p[0] for p in pts]
    for i in range(1, len(pts)):
        t1, p1, bid1, ask1, vol1 = pts[i]
        dif = p1 - pts[i - 1][1]
        if abs(dif) < UMBRAL or not (PMIN <= p1 <= PMAX) or not libro_valido(bid1, ask1):
            continue
        for h in HORIZONTES:
            j = bisect.bisect_left(tiempos, t1 + timedelta(hours=h))
            if j >= len(pts):
                continue
            _, _, bid2, ask2, _ = pts[j]
            if not libro_valido(bid2, ask2):
                continue
            comprar_si = (dif < 0)  # revertir: si bajó, compro Sí
            for estrategia, sube in (("revertir", comprar_si), ("seguir", not comprar_si)):
                if sube:   # Sí
                    compra, venta = ask1, bid2
                else:      # No
                    compra, venta = 1 - bid1, 1 - ask2
                pnl = (APUESTA / compra) * venta - APUESTA
                for grupo in ("todos", tramo(vol1)):
                    res[(estrategia, h, grupo)].append(pnl)

print("\nSimulación con spread real, 20 USD por señal:")
for estrategia in ("revertir", "seguir"):
    for h in HORIZONTES:
        print(f"\n=== {estrategia.upper()} | cerrar a las {h} h ===")
        for grupo in ("todos", "menos de 1.000 USD", "1.000 USD o más"):
            v = res.get((estrategia, h, grupo), [])
            if not v:
                continue
            gano = sum(1 for x in v if x > 0) / len(v)
            print(f"  {grupo}: {len(v)} operaciones, ganó {gano:.0%}, "
                  f"total {sum(v):+.0f} USD ({sum(v)/len(v):+.2f} por operación)")