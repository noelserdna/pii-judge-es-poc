"""Figura: qué encuentra un detector «que se pasa» en 10 sentencias reales.

Lee solo las cifras agregadas y públicas de reports/chequeo-realidad.json.

Uso:  uv run --group docs python tools/figuras/candidatos_por_tipo.py
Salida: docs/guia/img/candidatos_por_tipo.png
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[2]
NOMBRES = {
    "PER": "Persona (spaCy + tratamientos)",
    "ORG": "Organización (spaCy)",
    "NUM_EXPEDIENTE": "Número con forma de expediente",
    "LOC": "Lugar (spaCy)",
    "TELEFONO": "Teléfono",
    "EMAIL": "Correo electrónico",
    "IBAN": "IBAN",
}


def main() -> None:
    d = json.loads((RAIZ / "reports" / "chequeo-realidad.json").read_text(encoding="utf-8"))
    por = {}
    for k, v in d["totales"]["por_etiqueta"].items():
        clave = k.split("+")[0]
        por[clave] = por.get(clave, 0) + v
    items = sorted(por.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(8, 3.8), dpi=150)
    barras = ax.barh([NOMBRES.get(k, k) for k, _ in items], [v for _, v in items], color="#3949ab")
    for b, (_, v) in zip(barras, items, strict=True):
        ax.text(b.get_width() + 15, b.get_y() + b.get_height() / 2, f"{v:,}".replace(",", "."), va="center", fontsize=9)
    ax.set_xlabel("Candidatos en 10 sentencias")
    ax.set_title(f"Detector v0: {d['totales']['candidatos']:,} candidatos en 10 sentencias".replace(",", "."), loc="left")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_xlim(0, max(v for _, v in items) * 1.15)
    fig.tight_layout()
    salida = RAIZ / "docs" / "guia" / "img" / "candidatos_por_tipo.png"
    fig.savefig(salida)
    print(salida)


if __name__ == "__main__":
    main()
