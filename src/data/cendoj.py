"""Pipeline del CENDOJ (Paso 3a): textos, manifiesto, particiones, candidatos, anotación e instancias.

Todo lo que contiene texto vive en data/cendoj/raw/ (no se publica). Lo publicable es:
- data/cendoj/manifiesto-cendoj.csv: ROJ, jurisdicción, órgano, partición y SHA-256 del texto;
- data/cendoj/annot/*.jsonl: anotaciones como posiciones, sin texto.
(La publicación espera a la respuesta del CENDOJ, ADR-018.)

Uso:
  python -m src.data.cendoj preparar  --raw data/cendoj/raw/conjunto
  python -m src.data.cendoj instancias --raw data/cendoj/raw/conjunto --anot <humano.json> --salida inst.jsonl
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

from src.annotate.muestreo import agrupar, marcar_contexto, muestrear
from src.data.instancias import contexto

SEMILLA = 20261107
MAX_GRUPOS = 70          # ADR-012
MAX_GRUPOS_PRESIDIO = 30
REPARTO = {"civil": (2, 1, 3), "penal": (3, 1, 2), "social": (2, 1, 3), "contencioso": (3, 1, 2)}  # train, cal, test


def nombre_fichero(roj: str) -> str:
    return roj.replace(" ", "_").replace("/", "_")


def extraer_textos(raw: Path) -> list[dict]:
    import pdfplumber

    refs = list(csv.DictReader((raw / "refs.csv").open(encoding="utf-8")))
    for r in refs:
        txt = raw / f"{nombre_fichero(r['roj'])}.txt"
        if not txt.exists():
            with pdfplumber.open(raw / f"{nombre_fichero(r['roj'])}.pdf") as pdf:
                txt.write_text("\n".join((p.extract_text() or "") for p in pdf.pages), encoding="utf-8", newline="\n")
        r["sha256"] = hashlib.sha256(txt.read_bytes()).hexdigest()
    return refs


def asignar_particiones(refs: list[dict], semilla: int = SEMILLA) -> None:
    """40/20/40 por documento, estratificado por jurisdicción, antes de anotar."""
    rng = random.Random(semilla)
    por_jur = defaultdict(list)
    for r in sorted(refs, key=lambda r: r["roj"]):
        por_jur[r["jurisdiccion"]].append(r)
    for jur, docs in sorted(por_jur.items()):
        rng.shuffle(docs)
        ntr, nca, _ = REPARTO[jur]
        for i, r in enumerate(docs):
            r["particion"] = "train" if i < ntr else "cal" if i < ntr + nca else "test"


def preparar(raw: Path, manifiesto: Path) -> None:
    from src.detector.run import detectar_documento

    refs = extraer_textos(raw)
    asignar_particiones(refs)
    with manifiesto.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh)
        w.writerow(["roj", "jurisdiccion", "organo", "particion", "sha256_texto", "fuente"])
        for r in sorted(refs, key=lambda r: r["roj"]):
            w.writerow([r["roj"], r["jurisdiccion"], r["organo"], r["particion"], r["sha256"],
                        "https://www.poderjudicial.es/search/indexAN.jsp"])

    instancias, resumen = [], defaultdict(int)
    for r in refs:
        texto = (raw / f"{nombre_fichero(r['roj'])}.txt").read_text(encoding="utf-8")
        cands = [{**c, "etiqueta": "+".join(c["det_label"])} for c in detectar_documento(r["roj"], texto)]
        resumen["candidatos"] += len(cands)
        sel = muestrear(agrupar(cands), MAX_GRUPOS, SEMILLA)
        instancias += [{**x, "fuente_det": "propio", "particion": r["particion"]} for x in sel]
        if r["particion"] == "test":  # detector no visto (exploratorio)
            propios = [(c["start"], c["end"]) for c in cands]
            pres = [{**c, "etiqueta": "+".join(c["det_label"])}
                    for c in detectar_documento(r["roj"], texto, presidio=True)
                    if not any(c["start"] < e and s < c["end"] for s, e in propios)]
            sel_p = muestrear(agrupar(pres), MAX_GRUPOS_PRESIDIO, SEMILLA)
            instancias += [{**x, "fuente_det": "presidio", "particion": "test_presidio"} for x in sel_p]
    rng = random.Random(SEMILLA)
    rng.shuffle(instancias)
    textos = {r["roj"]: (raw / f"{nombre_fichero(r['roj'])}.txt").read_text(encoding="utf-8") for r in refs}
    with (raw / "anotar.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["id", "contexto", "etiqueta", "categoria", "rol", "nota"])
        for i, x in enumerate(instancias, 1):
            w.writerow([f"A{i:04d}", marcar_contexto(textos[x["doc_id"]], x["start"], x["end"]), "", "", "", ""])
    with (raw / "clave.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for i, x in enumerate(instancias, 1):
            fh.write(json.dumps({"id": f"A{i:04d}", "doc_id": x["doc_id"], "particion": x["particion"],
                                 "grupo": x["grupo"], "n_menciones": x["n_menciones"], "start": x["start"],
                                 "end": x["end"], "detector": x["detector"], "det_label": x["det_label"],
                                 "score": x["score"], "fuente_det": x["fuente_det"]}, ensure_ascii=False) + "\n")
    # grupos completos (todas las menciones) para propagar en train
    with (raw / "grupos_train.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in refs:
            if r["particion"] != "train":
                continue
            cands = [{**c, "etiqueta": "+".join(c["det_label"])} for c in detectar_documento(r["roj"], textos[r["roj"]])]
            for clave, ms in agrupar(cands).items():
                fh.write(json.dumps({"grupo": "|".join(clave), "menciones": [
                    {k: m[k] for k in ("start", "end", "detector", "det_label", "score")} for m in ms]},
                    ensure_ascii=False) + "\n")
    resumen.update({"documentos": len(refs), "instancias": len(instancias),
                    "por_particion": dict(sorted({p: sum(x["particion"] == p for x in instancias)
                                                  for p in {x["particion"] for x in instancias}}.items()))})
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


def instancias(raw: Path, anot_path: Path) -> list[dict]:
    """Instancias anotadas del CENDOJ. AMBIGUO y EXCLUIDO_PLACEHOLDER se excluyen.
    En train, la etiqueta se propaga a todas las menciones del grupo (ADR-012)."""
    refs = {r["roj"]: r for r in csv.DictReader((raw / "refs.csv").open(encoding="utf-8"))}
    anot = json.loads(anot_path.read_text(encoding="utf-8"))
    clave = [json.loads(linea) for linea in (raw / "clave.jsonl").open(encoding="utf-8")]
    grupos_train = {}
    if (raw / "grupos_train.jsonl").exists():
        for linea in (raw / "grupos_train.jsonl").open(encoding="utf-8"):
            g = json.loads(linea)
            grupos_train[g["grupo"]] = g["menciones"]
    textos = {}
    out = []
    for k in clave:
        a = anot.get(k["id"])
        if not a or a["etiqueta"] not in ("SI", "NO"):
            continue
        doc = k["doc_id"]
        if doc not in textos:
            textos[doc] = (raw / f"{nombre_fichero(doc)}.txt").read_text(encoding="utf-8")
        menciones = [k]
        if k["particion"] == "train" and k["grupo"] in grupos_train:
            menciones = grupos_train[k["grupo"]]
        for j, m in enumerate(menciones):
            ctx, i, f = contexto(textos[doc], m["start"], m["end"])
            out.append({
                "id": f"cendoj:{k['id']}" + (f":{j}" if len(menciones) > 1 else ""),
                "fuente": "cendoj", "doc_id": doc, "particion": k["particion"], "grupo_eval": doc,
                "estrato": refs[doc]["jurisdiccion"], "contexto": ctx, "span_ini": i, "span_fin": f,
                "span": textos[doc][m["start"]:m["end"]], "y": int(a["etiqueta"] == "SI"),
                "categoria": a.get("categoria", ""), "rol": a.get("rol", ""), "det_label": m["det_label"],
                "detector": m["detector"], "score": m["score"], "fuente_det": k["fuente_det"],
                "organo": refs[doc]["organo"],
            })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["preparar", "instancias"])
    ap.add_argument("--raw", type=Path, default=Path("data/cendoj/raw/conjunto"))
    # hasta que conteste el CENDOJ (ADR-018) el manifiesto se queda en local, dentro de raw/
    ap.add_argument("--manifiesto", type=Path, default=Path("data/cendoj/raw/manifiesto-cendoj.csv"))
    ap.add_argument("--anot", type=Path)
    ap.add_argument("--salida", type=Path)
    a = ap.parse_args()
    if a.accion == "preparar":
        preparar(a.raw, a.manifiesto)
    else:
        from src.data.instancias import guardar

        xs = instancias(a.raw, a.anot)
        guardar(xs, a.salida)
        print(len(xs), "instancias")


if __name__ == "__main__":
    main()
