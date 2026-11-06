"""Cálculo del tamaño muestral para el criterio C2 (falsos descartes).

Pregunta: si en el conjunto de test hay n positivos y el modelo descarta k por error,
¿cuál es la cota superior unilateral al 95 % (Clopper-Pearson) de la tasa real de
falsos descartes? El criterio C2 exige tasa puntual ≤ 1 % y cota superior ≤ 2,5 %.

Uso:  uv run python tools/tamano_muestral.py
"""

from scipy.stats import beta

ALFA = 0.05  # unilateral


def cota_superior(k: int, n: int) -> float:
    """Cota superior unilateral (1-ALFA) de Clopper-Pearson para k fallos en n."""
    return 1.0 if k >= n else float(beta.ppf(1 - ALFA, k + 1, n - k))


def n_minimo_regla_del_tres(objetivo: float) -> int:
    n = 1
    while cota_superior(0, n) > objetivo:
        n += 1
    return n


def main() -> None:
    print("Cota superior CP 95 % (unilateral) de la tasa de falsos descartes")
    print(f"{'n':>6} | " + " | ".join(f"k={k:<2d}" for k in range(0, 8)))
    for n in (50, 100, 150, 300, 500, 700, 1000):
        print(f"{n:>6} | " + " | ".join(f"{100 * cota_superior(k, n):4.2f}%" for k in range(0, 8)))
    for obj in (0.01, 0.025):
        print(f"\nn mínimo con 0 fallos para cota ≤ {100 * obj:.1f} %: {n_minimo_regla_del_tres(obj)}")
    for n in (500, 600, 700):
        kmax = max(k for k in range(n) if k / n <= 0.01 and cota_superior(k, n) <= 0.025) \
            if any(k / n <= 0.01 and cota_superior(k, n) <= 0.025 for k in range(n)) else None
        print(f"n={n}: máximo de falsos descartes que aún «pasa» C2 = {kmax}")


if __name__ == "__main__":
    main()
