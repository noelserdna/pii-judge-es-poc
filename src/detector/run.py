"""Ejecuta el detector sobre una carpeta de textos y escribe `candidates.jsonl`.

Cada línea: {doc_id, cand_id, start, end, span, detector[], det_label[], score, context_start, context_end}
El contexto no se guarda como texto (se reconstruye con las posiciones), para que el fichero
de candidatos de documentos públicos pueda manejarse sin duplicar fragmentos.

Uso:
  uv run --group detector python -m src.detector.run --entrada DIR_TXT --salida candidates.jsonl [--presidio]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .merge import fusionar
from .ner import detectar_ner, detectar_tratamientos
from .regex_rules import detectar as detectar_regex
from .tipos import Candidato

VENTANA = 200


def detectar_propio(texto: str, usar_ner: bool = True) -> list[Candidato]:
    cands = detectar_regex(texto) + detectar_tratamientos(texto)
    if usar_ner:
        cands += detectar_ner(texto)
    return fusionar(cands)


def detectar_documento(doc_id: str, texto: str, presidio: bool = False, usar_ner: bool = True) -> list[dict]:
    if presidio:
        from .presidio_run import detectar_presidio

        cands = fusionar(detectar_presidio(texto))
    else:
        cands = detectar_propio(texto, usar_ner)
    return [
        {
            "doc_id": doc_id,
            "cand_id": f"{doc_id}:{c.start}-{c.end}",
            "start": c.start,
            "end": c.end,
            "span": texto[c.start : c.end],
            "detector": c.detector,
            "det_label": c.det_label,
            "score": c.score,
            "context_start": max(0, c.start - VENTANA),
            "context_end": min(len(texto), c.end + VENTANA),
        }
        for c in cands
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", type=Path, required=True, help="carpeta con ficheros .txt")
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--presidio", action="store_true")
    a = ap.parse_args()
    n = 0
    with a.salida.open("w", encoding="utf-8") as fh:
        for ruta in sorted(a.entrada.glob("*.txt")):
            for fila in detectar_documento(ruta.stem, ruta.read_text(encoding="utf-8"), a.presidio):
                fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
                n += 1
    print(f"{n} candidatos -> {a.salida}")


if __name__ == "__main__":
    main()
