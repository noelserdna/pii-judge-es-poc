"""Figura: cuántos positivos hacen falta para afirmar una tasa de falsos descartes.

Dibuja la cota superior unilateral al 95 % (Clopper-Pearson) frente al número de
positivos n, para 0, 1, 3 y 5 falsos descartes observados, con las líneas del 1 %
y del 2,5 % del criterio C2.

Uso:  uv run --group docs python tools/figuras/regla_del_tres.py
Salida: docs/guia/img/regla_del_tres.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta

SALIDA = Path(__file__).resolve().parents[2] / "docs" / "guia" / "img" / "regla_del_tres.png"


def cota(k: int, n: np.ndarray) -> np.ndarray:
    return beta.ppf(0.95, k + 1, n - k)


def main() -> None:
    n = np.arange(20, 1001)
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    colores = ["#3949ab", "#00897b", "#f9a825", "#e53935"]
    for k, color in zip((0, 1, 3, 5), colores):
        validos = n > k
        ax.plot(n[validos], 100 * cota(k, n[validos]), color=color, lw=2,
                label=f"{k} falso{'s' if k != 1 else ''} descarte{'s' if k != 1 else ''} observado{'s' if k != 1 else ''}")
    ax.axhline(1.0, color="#555", ls="--", lw=1)
    ax.axhline(2.5, color="#555", ls=":", lw=1)
    ax.text(1000, 1.05, "1 %", ha="right", va="bottom", fontsize=9, color="#555")
    ax.text(1000, 2.55, "2,5 % (límite de C2)", ha="right", va="bottom", fontsize=9, color="#555")
    ax.axvline(299, color="#3949ab", lw=0.8, alpha=0.5)
    ax.annotate("299 positivos sin ningún fallo\n→ cota = 1 % (regla del tres)", xy=(299, 1.0), xytext=(340, 5.2),
                fontsize=9, arrowprops={"arrowstyle": "->", "color": "#3949ab"}, color="#3949ab")
    ax.axvline(500, color="#e53935", lw=0.8, alpha=0.5)
    ax.annotate("500 positivos: C2 pasa\ncon hasta 5 fallos", xy=(500, 2.09), xytext=(600, 6.5),
                fontsize=9, arrowprops={"arrowstyle": "->", "color": "#e53935"}, color="#e53935")
    ax.set_ylim(0, 12)
    ax.set_xlim(20, 1000)
    ax.set_xlabel("Positivos en el conjunto de test (n)")
    ax.set_ylabel("Cota superior al 95 % de la tasa\nde falsos descartes (%)")
    ax.set_title("¿Cuántos positivos hacen falta para poder afirmar «falsos descartes ≤ 1 %»?")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.grid(alpha=0.25)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA)
    print(SALIDA)


if __name__ == "__main__":
    main()
