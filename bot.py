import csv
import json
import os
import requests
from datetime import datetime, timezone

URL = "https://gamma-api.polymarket.com/markets"
ARCHIVO = "precios.json"
LECTURAS = "lecturas.csv"
NOMBRES = "mercados.json"
UMBRAL = 0.02  # avisar si el precio cambia 2 puntos o más

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def enviar_telegram(texto):
    if not TOKEN or not CHAT_ID:
        print("Faltan los secrets de Telegram, no se envió el aviso.")
        return
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto},
        timeout=15,
    )
    print(f"Telegram respondió: {r.status_code}")


def precio_si(m):
    try:
        resultados = json.loads(m["outcomes"])
        precios = [float(p) for p in json.loads(m["outcomePrices"])]
        return precios[resultados.index("Yes")]
    except (KeyError, TypeError, ValueError):
        return None


def volumen(m, clave):
    try:
        return float(m[clave])
    except (KeyError, TypeError, ValueError):
        return ""


mercados = []
for offset in range(0, 1000, 500):
    params = {"active": "true", "closed": "false", "limit": 500, "offset": offset}
    pagina = requests.get(URL, params=params, timeout=15).json()
    if not pagina:
        break
    mercados.extend(pagina)

actuales = {}
vols = {}
for m in mercados:
    p = precio_si(m)
    if p is not None and "id" in m:
        id_ = str(m["id"])
        actuales[id_] = {"pregunta": m.get("question", ""), "precio": p}
        vols[id_] = (volumen(m, "volume24hr"), volumen(m, "volumeNum"))

print(f"Mercados leídos: {len(actuales)}")

# Guardar cada lectura sin pisar las anteriores
ahora_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
nuevo = not os.path.exists(LECTURAS)
with open(LECTURAS, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if nuevo:
        w.writerow(["fecha", "id", "precio", "volumen_24h", "volumen_total"])
    for id_, d in actuales.items():
        w.writerow([ahora_utc, id_, d["precio"], vols[id_][0], vols[id_][1]])

# Nombres de los mercados, guardados aparte para no repetirlos en cada fila
nombres = {}
if os.path.exists(NOMBRES):
    with open(NOMBRES, encoding="utf-8") as f:
        nombres = json.load(f)
for id_, d in actuales.items():
    nombres[id_] = d["pregunta"]
with open(NOMBRES, "w", encoding="utf-8") as f:
    json.dump(nombres, f, ensure_ascii=False)

# Alertas
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
    if cambios:
        lineas = ["Movimientos en Polymarket:"]
        for dif, pregunta, antes, ahora in cambios[:10]:
            lineas.append(f"{dif:+.3f} | {antes:.3f} -> {ahora:.3f} | {pregunta}")
        texto = "\n".join(lineas)
        print(texto)
        enviar_telegram(texto)
else:
    print("Primera corrida: guardé los precios como punto de partida.")

with open(ARCHIVO, "w") as f:
    json.dump(actuales, f)