import argparse
import glob
import json
import os
import time

from agente import ejecutar_caso


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="+", required=True)
    ap.add_argument("--repeticiones", type=int, default=5)
    ap.add_argument("--limite", type=int, default=0,
                    help="Solo los N primeros casos (para pruebas rápidas)")
    a = ap.parse_args()

    rutas = sorted(glob.glob(os.path.join("casos", "*.json")))
    if a.limite:
        rutas = rutas[:a.limite]
    casos = []
    for ruta in rutas:
        with open(ruta, encoding="utf-8") as f:
            casos.append(json.load(f))

    os.makedirs("resultados", exist_ok=True)

    for modelo in a.modelos:
        nombre = modelo.replace(":", "_").replace("/", "_")
        salida = os.path.join("resultados", nombre + ".jsonl")
        total = len(casos) * a.repeticiones
        hecho = 0
        inicio = time.time()
        print("Modelo:", modelo, "|", total, "ejecuciones")

        with open(salida, "w", encoding="utf-8") as f:
            for caso in casos:
                for rep in range(1, a.repeticiones + 1):
                    res = ejecutar_caso(modelo, caso)
                    res["repeticion"] = rep
                    res["tipo"] = caso.get("tipo")
                    res["soporte"] = caso.get("soporte")
                    f.write(json.dumps(res, ensure_ascii=False) + "\n")
                    f.flush()
                    hecho += 1
                    if hecho % 10 == 0 or hecho == total:
                        minutos = (time.time() - inicio) / 60
                        print("  ", hecho, "/", total, "-", round(minutos, 1), "min")

        print("Guardado en", salida)


if __name__ == "__main__":
    main()