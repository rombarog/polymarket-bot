import csv
import json
import subprocess

ARCHIVO = "precios.json"

# Lista de commits que tocaron precios.json, con su fecha
salida = subprocess.run(
    ["git", "log", "--format=%H %cI", "--", ARCHIVO],
    capture_output=True, text=True, check=True,
).stdout.strip().splitlines()

commits = [linea.split(" ", 1) for linea in salida]
commits.reverse()  # del más viejo al más nuevo

filas = 0
with open("historial.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["fecha", "id", "pregunta", "precio"])
    for hash_, fecha in commits:
        try:
            contenido = subprocess.run(
                ["git", "show", f"{hash_}:{ARCHIVO}"],
                capture_output=True, text=True, check=True,
            ).stdout
            datos = json.loads(contenido)
        except Exception:
            continue
        for id_, d in datos.items():
            w.writerow([fecha, id_, d["pregunta"], d["precio"]])
            filas += 1

print(f"Commits leídos: {len(commits)}")
print(f"Filas guardadas en historial.csv: {filas}")