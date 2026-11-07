"""Construye la tabla de instancias (una fila por candidato a juzgar) a partir de las fuentes.

Formato común para sintéticos y CENDOJ:
  id, fuente (synth|cendoj), doc_id, particion, grupo_eval (unidad de bootstrap), estrato
  (familia o jurisdicción), contexto, span_ini, span_fin (dentro de `contexto`), span,
  y (1 = dato personal), categoria, rol, det_label, detector, score
"""

from __future__ import annotations

import json
from pathlib import Path

VENTANA = 200


def contexto(texto: str, start: int, end: int, ventana: int = VENTANA) -> tuple[str, int, int]:
    a, b = max(0, start - ventana), min(len(texto), end + ventana)
    return texto[a:b], start - a, end - a


def instancias_sinteticas(carpeta: Path) -> list[dict]:
    docs = {}
    with (carpeta / "documentos.jsonl").open(encoding="utf-8") as fh:
        for linea in fh:
            d = json.loads(linea)
            docs[d["doc_id"]] = d
    out = []
    with (carpeta / "candidatos.jsonl").open(encoding="utf-8") as fh:
        for linea in fh:
            c = json.loads(linea)
            d = docs[c["doc_id"]]
            ctx, i, f = contexto(d["texto"], c["start"], c["end"])
            out.append({
                "id": f"synth:{c['cand_id']}",
                "fuente": "synth",
                "doc_id": c["doc_id"],
                "particion": c["particion"],
                "grupo_eval": c["doc_id"],
                "estrato": c["familia"],
                "contexto": ctx,
                "span_ini": i,
                "span_fin": f,
                "span": c["span"],
                "y": int(c["etiqueta"] == "SI"),
                "categoria": c["categoria"],
                "rol": c["rol"],
                "det_label": c["det_label"],
                "detector": c["detector"],
                "score": c["score"],
            })
    return out


def guardar(instancias: list[dict], ruta: Path) -> None:
    with ruta.open("w", encoding="utf-8", newline="\n") as fh:
        for x in instancias:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")


def cargar(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as fh:
        return [json.loads(linea) for linea in fh]


def por_particion(instancias: list[dict], particion: str) -> list[dict]:
    return [x for x in instancias if x["particion"] == particion]
