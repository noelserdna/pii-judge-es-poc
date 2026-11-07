"""Métricas y criterios preregistrados (protocolo §6–§8).

Convención: puntuación ≥ τ → se trata como dato personal; puntuación < τ → se descarta.
- FNR = positivos descartados / positivos  (falsos descartes)
- TNR = negativos descartados / negativos  (% de falsos positivos eliminados)
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from scipy.stats import beta

FNR_OBJETIVO = 0.01


def umbral_fnr(scores: np.ndarray, y: np.ndarray, fnr: float = FNR_OBJETIVO) -> float:
    """Mayor τ que deja FNR ≤ fnr en (scores, y): se permiten floor(fnr·P) positivos por debajo."""
    pos = np.sort(np.asarray(scores)[np.asarray(y) == 1])
    if len(pos) == 0:
        raise ValueError("no hay positivos para fijar el umbral")
    k = math.floor(fnr * len(pos))
    return float(pos[k])  # exactamente k positivos (o menos, con empates) quedan estrictamente por debajo


def tasas(scores: np.ndarray, y: np.ndarray, tau: float) -> dict:
    s, y = np.asarray(scores), np.asarray(y)
    descartado = s < tau
    P, N = int((y == 1).sum()), int((y == 0).sum())
    fn, tn = int((descartado & (y == 1)).sum()), int((descartado & (y == 0)).sum())
    return {"P": P, "N": N, "FN": fn, "TN": tn,
            "FNR": fn / P if P else float("nan"), "TNR": tn / N if N else float("nan")}


def cp_superior(k: int, n: int, alfa: float = 0.05) -> float:
    """Cota superior unilateral (1-alfa) de Clopper-Pearson."""
    return 1.0 if k >= n else float(beta.ppf(1 - alfa, k + 1, n - k))


def bootstrap_pareado(grupos: list[str], y: np.ndarray, scores: dict[str, np.ndarray], taus: dict[str, float],
                      n_rep: int = 2000, semilla: int = 0) -> dict[str, np.ndarray]:
    """Remuestrea **grupos** (documentos) con reemplazo; devuelve TNR y FNR por réplica y modelo.

    Las mismas réplicas se usan para todos los modelos (bootstrap pareado).
    """
    rng = np.random.default_rng(semilla)
    idx_por_grupo: dict[str, list[int]] = defaultdict(list)
    for i, g in enumerate(grupos):
        idx_por_grupo[g].append(i)
    claves = sorted(idx_por_grupo)
    idx = [np.array(idx_por_grupo[g]) for g in claves]
    y = np.asarray(y)
    out = {f"{m}_{t}": np.empty(n_rep) for m in scores for t in ("TNR", "FNR")}
    for r in range(n_rep):
        sel = np.concatenate([idx[j] for j in rng.integers(0, len(claves), len(claves))])
        yr = y[sel]
        for m, s in scores.items():
            t = tasas(np.asarray(s)[sel], yr, taus[m])
            out[f"{m}_TNR"][r], out[f"{m}_FNR"][r] = t["TNR"], t["FNR"]
    return out


def ic95(x: np.ndarray) -> tuple[float, float]:
    x = x[~np.isnan(x)]
    return float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))


@dataclass
class Veredicto:
    criterio: str
    punto: float
    inferior: float | None
    superior: float | None
    veredicto: str  # pasa | no concluyente | no pasa | no aplicable

    def dict(self) -> dict:
        return self.__dict__.copy()


def c1(tnr_punto: float, tnr_rep: np.ndarray, umbral: float = 0.25) -> Veredicto:
    lo, hi = ic95(tnr_rep)
    v = "pasa" if lo >= umbral else ("no concluyente" if tnr_punto >= umbral else "no pasa")
    return Veredicto("C1", tnr_punto, lo, hi, v)


def c2(fn: int, p: int, minimo_p: int = 500, umbral: float = 0.01, cota: float = 0.025) -> Veredicto:
    punto = fn / p
    sup = cp_superior(fn, p)
    if punto > umbral:
        v = "no pasa"
    elif p < minimo_p or sup > cota:
        v = "no concluyente"
    else:
        v = "pasa"
    return Veredicto("C2", punto, 0.0, sup, v)


def c3(delta_punto: float, delta_rep: np.ndarray, margen: float = 0.05) -> Veredicto:
    lo, hi = ic95(delta_rep)
    if delta_punto < margen:
        v = "no pasa"
    elif lo > 0:
        v = "pasa"
    else:
        v = "no concluyente"
    return Veredicto("C3", delta_punto, lo, hi, v)


def riesgo_cobertura(s_cal, y_cal, s_eval, y_eval, epsilons=(0.01, 0.02, 0.05)) -> list[dict]:
    filas = []
    for e in epsilons:
        tau = umbral_fnr(np.asarray(s_cal), np.asarray(y_cal), e)
        t = tasas(s_eval, y_eval, tau)
        filas.append({"epsilon": e, "tau": tau, **t, "FNR_CP_sup": cp_superior(t["FN"], t["P"]) if t["P"] else None})
    return filas
