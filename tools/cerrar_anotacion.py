"""Después de anotar: congelado, instancias completas y anotaciones publicables.

1. Comprueba que todas las instancias están anotadas y resume etiquetas, ambiguos y tiempos.
2. Calcula el SHA-256 del fichero de anotación (va a la bitácora y al tag `anotacion-congelada`).
3. Escribe las anotaciones como **posiciones sin texto** en data/cendoj/annot/anotaciones.jsonl
   (publicables cuando conteste el CENDOJ, ADR-018; hasta entonces el fichero no se versiona).
4. Construye data/cendoj/raw/instancias_completas.jsonl = sintéticos + CENDOJ (local; contiene texto).

Uso:  uv run python tools/cerrar_anotacion.py --anot data/cendoj/raw/conjunto/anotacion_humano.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.data.cendoj import instancias as instancias_cendoj
from src.data.instancias import guardar, instancias_sinteticas


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anot", type=Path, required=True)
    ap.add_argument("--raw", type=Path, default=RAIZ / "data/cendoj/raw/conjunto")
    a = ap.parse_args()

    anot = json.loads(a.anot.read_text(encoding="utf-8"))
    clave = [json.loads(linea) for linea in (a.raw / "clave.jsonl").open(encoding="utf-8")]
    faltan = [k["id"] for k in clave if k["id"] not in anot]
    etiquetas = Counter(v["etiqueta"] for v in anot.values())
    ms = [v["ms"] for v in anot.values() if v.get("ms")]
    sha = hashlib.sha256(a.anot.read_bytes()).hexdigest()
    resumen = {
        "anotadas": len(anot), "total": len(clave), "faltan": len(faltan),
        "etiquetas": dict(etiquetas),
        "ambiguos_pct": round(100 * etiquetas.get("AMBIGUO", 0) / max(1, len(anot)), 2),
        "mediana_s": round(statistics.median(ms) / 1000, 1) if ms else None,
        "horas_netas": round(sum(ms) / 3_600_000, 2),
        "sha256_anotacion": sha,
    }
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    if faltan:
        sys.exit(f"Faltan {len(faltan)} instancias por anotar (p. ej. {faltan[:5]}). No se congela nada.")

    destino = RAIZ / "data/cendoj/annot/anotaciones.jsonl"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="\n") as fh:
        for k in clave:
            v = anot[k["id"]]
            fh.write(json.dumps({"id": k["id"], "doc_id": k["doc_id"], "particion": k["particion"],
                                 "start": k["start"], "end": k["end"], "etiqueta": v["etiqueta"],
                                 "categoria": v.get("categoria", ""), "rol": v.get("rol", ""),
                                 "fuente_det": k["fuente_det"]}, ensure_ascii=False) + "\n")
    xs = instancias_sinteticas(RAIZ / "data/synth") + instancias_cendoj(a.raw, a.anot)
    guardar(xs, RAIZ / "data/cendoj/raw/instancias_completas.jsonl")
    por = Counter((x["fuente"], x["particion"], x["y"]) for x in xs)
    print("instancias:", len(xs))
    for k in sorted(por):
        print("  ", k, por[k])
    (RAIZ / "data/cendoj/raw/congelado.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1),
                                                          encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
