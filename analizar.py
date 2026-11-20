import glob
import json
import math
import os
from collections import defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centro - margen), min(1.0, centro + margen)


def fmt(k, n):
    if n == 0:
        return "sin datos"
    lo, hi = wilson(k, n)
    return "%d/%d = %.0f %% (IC 95 %%: %.0f-%.0f %%)" % (k, n, 100 * k / n, 100 * lo, 100 * hi)


def main():
    for ruta in sorted(glob.glob(os.path.join("resultados", "*.jsonl"))):
        filas = []
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                filas.append(json.loads(linea))

        ataques = [r for r in filas if r.get("tipo") == "ataque"]
        limpios = [r for r in filas if r.get("tipo") == "limpio"]
        modelo = filas[0]["modelo"] if filas else ruta

        print("=" * 60)
        print("Modelo:", modelo)
        print("Ejecuciones:", len(filas))

        exito = sum(1 for r in ataques if r["ataque_exitoso"])
        print("\nAtaques exitosos (total):", fmt(exito, len(ataques)))

        por_tec = defaultdict(list)
        por_sop = defaultdict(list)
        for r in ataques:
            por_tec[r["tecnica"]].append(r)
            por_sop[r["soporte"]].append(r)

        print("\nPor técnica:")
        for t, rs in sorted(por_tec.items()):
            print("  %-15s %s" % (t, fmt(sum(1 for r in rs if r["ataque_exitoso"]), len(rs))))

        print("\nPor soporte:")
        for s, rs in sorted(por_sop.items()):
            print("  %-15s %s" % (s, fmt(sum(1 for r in rs if r["ataque_exitoso"]), len(rs))))

        usa = sum(1 for r in limpios if r["llamadas"])
        print("\nCasos limpios con llamadas a herramientas sin motivo:", fmt(usa, len(limpios)))

        sin_resp = sum(1 for r in filas if r["respuesta"] is None)
        errores = sum(1 for r in filas if r["error"])
        print("Ejecuciones sin respuesta final:", sin_resp, "| con error:", errores)
        print()

    print("Aviso: las 5 repeticiones de un mismo caso no son independientes,")
    print("así que los intervalos son optimistas. Hay que decirlo en el README.")


if __name__ == "__main__":
    main()