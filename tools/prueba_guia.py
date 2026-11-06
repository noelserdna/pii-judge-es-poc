"""Paso 1: prueba en seco de la guía de anotación sobre las sentencias del chequeo.

Toma los candidatos del chequeo de realidad, los agrupa (ADR-012), muestrea
6 grupos por sentencia (60 en total) y genera un CSV para anotar a mano.
Las 10 sentencias del chequeo quedan fuera de calibración y test, así que
esta prueba no contamina la evaluación.

Salida (local, NO se publica; contiene texto):
  data/cendoj/raw/chequeo/prueba_guia_anotar.csv   (para abrir en Excel; separador «;»)
  data/cendoj/raw/chequeo/prueba_guia_clave.csv    (metadatos: grupo, etiqueta del detector)

Uso:  uv run python tools/prueba_guia.py
"""

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.annotate.muestreo import agrupar, marcar_contexto, muestrear  # noqa: E402

DIR = RAIZ / "data" / "cendoj" / "raw" / "chequeo"
SEMILLA = 20261107
POR_DOC = 6


def main() -> None:
    filas = list(csv.DictReader((DIR / "candidatos.csv").open(encoding="utf-8")))
    textos = {}
    cands = []
    for f in filas:
        doc = f["roj"]
        if doc not in textos:
            textos[doc] = (DIR / f"{doc.replace(' ', '_').replace('/', '_')}.txt").read_text(encoding="utf-8")
        cands.append({"doc_id": doc, "span": textos[doc][int(f["start"]):int(f["end"])],
                      "start": int(f["start"]), "end": int(f["end"]), "etiqueta": f["etiqueta"],
                      "detector": f["detector"]})

    instancias = muestrear(agrupar(cands), max_por_doc=POR_DOC, semilla=SEMILLA)
    # orden aleatorio global para que el anotador no vea bloques por documento
    import random
    random.Random(SEMILLA).shuffle(instancias)

    with (DIR / "prueba_guia_anotar.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["id", "contexto", "etiqueta", "categoria", "rol", "nota"])
        for i, x in enumerate(instancias, 1):
            w.writerow([f"P{i:03d}", marcar_contexto(textos[x["doc_id"]], x["start"], x["end"]), "", "", "", ""])
    with (DIR / "prueba_guia_clave.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "doc_id", "grupo", "n_menciones", "etiqueta_detector", "detector", "start", "end"])
        for i, x in enumerate(instancias, 1):
            w.writerow([f"P{i:03d}", x["doc_id"], x["grupo"], x["n_menciones"], x["etiqueta"], x["detector"],
                        x["start"], x["end"]])
    print(f"{len(instancias)} instancias -> {DIR / 'prueba_guia_anotar.csv'}")


if __name__ == "__main__":
    main()
