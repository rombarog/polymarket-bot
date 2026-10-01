import json
import os
import requests

URL = "https://gamma-api.polymarket.com/markets"
ARCHIVO = "precios.json"
UMBRAL = 0.02  # avisar si el precio cambia 2 puntos o más

mercados = []
for offset in range(0, 1000, 500):
    params = {"active": "true", "closed": "false", "limit": 500, "offset": offset}
    pagina = requests.get(URL, params=params, timeout=15).json()
    if not pagina:
        break
    mercados.extend(pagina)

def precio_si(m):
    try:
        resultados = json.loads(m["outcomes"])
        precios = [float(p) for p in json.loads(m["outcomePrices"])]
        return precios[resultados.index("Yes")]
    except (KeyError, TypeError, ValueError):
        return None

actuales = {}
for m in mercados:
    p = precio_si(m)
    if p is not None and "id" in m:
        actuales[str(m["id"])] = {"pregunta": m.get("question", ""), "precio": p}

print(f"Mercados leídos: {len(actuales)}")

if os.path.exists(ARCHIVO):
    with open(ARCHIVO) as f:
        anteriores = json.load(f)
    cambios = []
    for id_, datos in actuales.items():
        if id_ in anteriores:
            dif = datos["precio"] - anteriores[id_]["precio"]
            if abs(dif) >= UMBRAL:
                cambios.append((dif, datos["pregunta"], anteriores[id_]["precio"], datos["precio"]))
    cambios.sort(key=lambda x: abs(x[0]), reverse=True)
    print(f"Mercados con cambio de {UMBRAL} o más: {len(cambios)}")
    for dif, pregunta, antes, ahora in cambios[:10]:
        print(f"{dif:+.3f} | {antes:.3f} -> {ahora:.3f} | {pregunta}")
else:
    print("Primera corrida: guardé los precios como punto de partida.")

with open(ARCHIVO, "w") as f:
    json.dump(actuales, f)