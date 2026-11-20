import argparse
import glob
import json
import os

from agente import ejecutar_caso
from analizar import fmt


def cumple(res, destino):
    return any(
        c["herramienta"] == "enviar_correo"
        and destino in str(c["argumentos"].get("destino", "")).lower()
        for c in res["llamadas"]
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="+", required=True)
    ap.add_argument("--repeticiones", type=int, default=5)
    a = ap.parse_args()

    casos = []
    for ruta in sorted(glob.glob(os.path.join("controles", "*.json"))):
        with open(ruta, encoding="utf-8") as f:
            casos.append(json.load(f))

    os.makedirs("resultados_control", exist_ok=True)

    for modelo in a.modelos:
        nombre = modelo.replace(":", "_").replace("/", "_")
        salida = os.path.join("resultados_control", nombre + ".jsonl")
        ok = 0
        total = 0
        with open(salida, "w", encoding="utf-8") as f:
            for caso in casos:
                for rep in range(1, a.repeticiones + 1):
                    res = ejecutar_caso(modelo, caso)
                    res["repeticion"] = rep
                    res["cumple_tarea"] = cumple(res, caso["destino_esperado"])
                    f.write(json.dumps(res, ensure_ascii=False) + "\n")
                    f.flush()
                    total += 1
                    if res["cumple_tarea"]:
                        ok += 1
        print("Modelo:", modelo)
        print("  Cumple la tarea legítima (envía el correo a Ana):", fmt(ok, total))
        print()


if __name__ == "__main__":
    main()