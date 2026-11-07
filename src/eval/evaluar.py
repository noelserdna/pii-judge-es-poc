"""Evaluación según el protocolo preregistrado (§6–§9).

1. Entrena la regresión logística en `train` y guarda sus predicciones (cal, test y test_*).
2. Lee las predicciones de los modelos afinados (`<modelo>__<variante>__f<fraccion>__s<semilla>.jsonl`).
3. Para cada modelo fija τ en Cal (FNR ≤ 1 %) y mide en T.
4. Candidato = DistilBETO «completa», fracción 1, semilla mediana por TNR en Cal.
5. Criterios C1–C3 con bootstrap pareado por documento; Nivel 2 (CENDOJ por rol y estrato);
   exploratorios (ablaciones, curva, techo, cortes sintético→CENDOJ y particiones test_*).

Uso:
  python -m src.eval.evaluar --instancias inst.jsonl --preds reports/predicciones --salida reports/metrics.json
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from src.baselines.logreg import RegresionLogistica
from src.eval.metrics import (
    bootstrap_pareado,
    c1,
    c2,
    c3,
    cp_superior,
    ic95,
    riesgo_cobertura,
    tasas,
    umbral_fnr,
)

CANDIDATO = "distilbert-base-spanish-uncased"
N_REP = 2000


def cargar_preds(carpeta: Path) -> dict[str, dict[str, float]]:
    out = {}
    for f in sorted(carpeta.glob("*.jsonl")):
        out[f.stem] = {json.loads(linea)["id"]: json.loads(linea)["p"] for linea in f.open(encoding="utf-8")}
    return out


def vec(xs, preds):
    return np.array([preds[x["id"]] for x in xs])


def resumen_modelo(nombre, preds, cal, test) -> dict:
    tau = umbral_fnr(vec(cal, preds), np.array([x["y"] for x in cal]))
    t_cal = tasas(vec(cal, preds), np.array([x["y"] for x in cal]), tau)
    t_test = tasas(vec(test, preds), np.array([x["y"] for x in test]), tau)
    return {"nombre": nombre, "tau": tau, "cal": t_cal, "test": t_test}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instancias", type=Path, required=True)
    ap.add_argument("--preds", type=Path, required=True)
    ap.add_argument("--salida", type=Path, required=True)
    a = ap.parse_args()

    xs = [json.loads(linea) for linea in a.instancias.open(encoding="utf-8")]
    part = defaultdict(list)
    for x in xs:
        part[x["particion"]].append(x)
    train, cal, test = part["train"], part["cal"], part["test"]
    extra = {p: v for p, v in part.items() if p.startswith("test_")}

    # 1. regresión logística (determinista) -> predicciones
    lr = RegresionLogistica().fit(train)
    a.preds.mkdir(parents=True, exist_ok=True)
    evaluables = [*cal, *test, *[x for v in extra.values() for x in v]]
    with (a.preds / "logreg__completa__f1__s0.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for x, p in zip(evaluables, lr.predict_proba(evaluables), strict=True):
            fh.write(json.dumps({"id": x["id"], "particion": x["particion"], "p": round(float(p), 6)}) + "\n")
    preds = cargar_preds(a.preds)

    resumenes = {n: resumen_modelo(n, p, cal, test) for n, p in preds.items()}

    # 2. candidato: semilla mediana por TNR en Cal
    semillas = sorted((r["cal"]["TNR"], n) for n, r in resumenes.items()
                      if n.startswith(f"{CANDIDATO}__completa__f1__"))
    if not semillas:
        raise SystemExit("no hay predicciones del candidato")
    cand = semillas[(len(semillas) - 1) // 2][1]
    lr_n = "logreg__completa__f1__s0"

    # 3. criterios
    y_t = np.array([x["y"] for x in test])
    grupos = [x["grupo_eval"] for x in test]
    sc = {"cand": vec(test, preds[cand]), "lr": vec(test, preds[lr_n])}
    taus = {"cand": resumenes[cand]["tau"], "lr": resumenes[lr_n]["tau"]}
    rep = bootstrap_pareado(grupos, y_t, sc, taus, n_rep=N_REP, semilla=2026)
    rc, rl = resumenes[cand]["test"], resumenes[lr_n]["test"]
    criterios = [
        c1(rc["TNR"], rep["cand_TNR"]).dict(),
        c2(rc["FN"], rc["P"]).dict(),
        c3(rc["TNR"] - rl["TNR"], rep["cand_TNR"] - rep["lr_TNR"]).dict(),
    ]

    # 4. Nivel 2: CENDOJ en T, global, por rol y por estrato
    def descriptivo(sub, nombre):
        if not sub:
            return None
        y = np.array([x["y"] for x in sub])
        t = tasas(vec(sub, preds[nombre]), y, resumenes[nombre]["tau"])
        t["FNR_CP_sup"] = cp_superior(t["FN"], t["P"]) if t["P"] else None
        return t

    ced = [x for x in test if x["fuente"] == "cendoj"]
    nivel2 = None
    if ced:
        nivel2 = {
            "global": descriptivo(ced, cand),
            "por_rol": {r: descriptivo([x for x in ced if x["y"] == 0 or x["rol"] == r], cand)
                        for r in sorted({x["rol"] for x in ced if x["y"] == 1})},
            "por_estrato": {e: descriptivo([x for x in ced if x["estrato"] == e], cand)
                            for e in sorted({x["estrato"] for x in ced})},
            "riesgo_cobertura": riesgo_cobertura(vec(cal, preds[cand]), [x["y"] for x in cal],
                                                 vec(ced, preds[cand]), [x["y"] for x in ced]),
        }
        r = bootstrap_pareado([x["grupo_eval"] for x in ced], np.array([x["y"] for x in ced]),
                              {"c": vec(ced, preds[cand])}, {"c": resumenes[cand]["tau"]}, n_rep=N_REP, semilla=7)
        nivel2["global"]["TNR_IC95"] = ic95(r["c_TNR"])

    # 5. exploratorio: resumen por configuración (mediana entre semillas)
    por_config = defaultdict(list)
    for n, r in resumenes.items():
        por_config[n.rsplit("__s", 1)[0]].append(r)
    exploratorio = {
        cfg: {"semillas": len(rs),
              "TNR_test_mediana": statistics.median(r["test"]["TNR"] for r in rs),
              "FNR_test_mediana": statistics.median(r["test"]["FNR"] for r in rs),
              "TNR_test_rango": [min(r["test"]["TNR"] for r in rs), max(r["test"]["TNR"] for r in rs)]}
        for cfg, rs in sorted(por_config.items())
    }
    # corte sintético→CENDOJ: τ fijado solo con Cal sintético
    cal_s = [x for x in cal if x["fuente"] == "synth"]
    if ced and cal_s:
        tau_s = umbral_fnr(vec(cal_s, preds[cand]), np.array([x["y"] for x in cal_s]))
        exploratorio["corte_sintetico_a_cendoj"] = {"tau": tau_s, **tasas(vec(ced, preds[cand]),
                                                    np.array([x["y"] for x in ced]), tau_s)}
    for p, v in extra.items():
        exploratorio[f"particion_{p}"] = {n: tasas(vec(v, preds[n]), np.array([x["y"] for x in v]), resumenes[n]["tau"])
                                          for n in (cand, lr_n) if all(x["id"] in preds[n] for x in v)}

    salida = {
        "candidato": cand,
        "tamanos": {"train": len(train), "cal": len(cal), "test": len(test),
                    "positivos_test": int(y_t.sum()), "negativos_test": int(len(y_t) - y_t.sum())},
        "criterios": criterios,
        "evidencia_trl3": f"{sum(c['veredicto'] == 'pasa' for c in criterios)}/3",
        "modelos": resumenes,
        "nivel2_cendoj": nivel2,
        "exploratorio": exploratorio,
        "bootstrap": {"replicas": N_REP, "unidad": "documento", "semilla": 2026},
    }
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    a.salida.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({"candidato": cand, "criterios": criterios, "evidencia_trl3": salida["evidencia_trl3"]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
