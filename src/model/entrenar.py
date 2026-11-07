"""Afinado del validador (protocolo §5) y exportación de predicciones.

Entrada al modelo (variante «completa»):
    "<forma> | <contexto izquierdo> [ <span> ] <contexto derecho>"
donde <forma> ∈ {inicial, todo, ninguna} describe las mayúsculas del span (señal para el
modelo uncased) y los corchetes son tokens que ya existen en el vocabulario (ADR-006).

Variantes (protocolo §9): completa · sin_mayuscula · solo_candidato · solo_contexto ·
sin_cendoj (entrena solo con sintéticos). --fraccion < 1 da la curva de aprendizaje
(se submuestrean documentos, no instancias).

Hiperparámetros fijos: 3 épocas, lr 3e-5, batch 32, max_len 192, warmup 10 %,
weight decay 0,01, último epoch. Se puede pedir acumulación (--acumular) si no cabe el batch.

Uso:
  python -m src.model.entrenar --instancias inst.jsonl --salida preds/ \
      --modelo dccuchile/distilbert-base-spanish-uncased --variante completa --semilla 13 --eval cal,test
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

VARIANTES = ("completa", "sin_mayuscula", "solo_candidato", "solo_contexto", "sin_cendoj")


def forma_mayusculas(span: str) -> str:
    letras = [c for c in span if c.isalpha()]
    if letras and all(c.isupper() for c in letras):
        return "todo"
    if span[:1].isupper():
        return "inicial"
    return "ninguna"


def texto_entrada(x: dict, variante: str) -> str:
    izq = x["contexto"][: x["span_ini"]]
    der = x["contexto"][x["span_fin"] :]
    span = x["contexto"][x["span_ini"] : x["span_fin"]]
    match variante:
        case "solo_candidato":
            return f"{forma_mayusculas(span)} | [ {span} ]"
        case "solo_contexto":
            return f"{izq} [ ] {der}"
        case "sin_mayuscula":
            return f"{izq} [ {span} ] {der}"
        case _:
            return f"{forma_mayusculas(span)} | {izq} [ {span} ] {der}"


def fijar_semilla(s: int) -> None:
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


def submuestrear_docs(xs: list[dict], fraccion: float, semilla: int) -> list[dict]:
    if fraccion >= 1:
        return xs
    docs = sorted({x["doc_id"] for x in xs})
    random.Random(semilla).shuffle(docs)
    elegidos = set(docs[: max(1, round(fraccion * len(docs)))])
    return [x for x in xs if x["doc_id"] in elegidos]


def cargador(tok, xs, variante, max_len, batch, barajar, semilla):
    textos = [texto_entrada(x, variante) for x in xs]
    enc = tok(textos, truncation=True, max_length=max_len)
    items = [{"input_ids": enc["input_ids"][i], "attention_mask": enc["attention_mask"][i], "labels": xs[i]["y"]}
             for i in range(len(xs))]

    def collate(b):
        out = tok.pad([{k: v for k, v in e.items() if k != "labels"} for e in b], return_tensors="pt")
        out["labels"] = torch.tensor([e["labels"] for e in b])
        return out

    g = torch.Generator().manual_seed(semilla)
    return DataLoader(items, batch_size=batch, shuffle=barajar, collate_fn=collate, generator=g)


@torch.no_grad()
def predecir(modelo, dl, dev) -> np.ndarray:
    modelo.eval()
    ps = []
    for b in dl:
        b = {k: v.to(dev) for k, v in b.items() if k != "labels"}
        ps.append(torch.softmax(modelo(**b).logits.float(), -1)[:, 1].cpu().numpy())
    return np.concatenate(ps) if ps else np.array([])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instancias", type=Path, required=True)
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--modelo", default="dccuchile/distilbert-base-spanish-uncased")
    ap.add_argument("--variante", choices=VARIANTES, default="completa")
    ap.add_argument("--semilla", type=int, default=13)
    ap.add_argument("--fraccion", type=float, default=1.0)
    ap.add_argument("--eval", default="cal,test", help="particiones a predecir, separadas por comas")
    ap.add_argument("--epocas", type=int, default=3)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--acumular", type=int, default=1)
    ap.add_argument("--max_len", type=int, default=192)
    ap.add_argument("--max_pasos", type=int, default=0, help="solo para pruebas de humo")
    a = ap.parse_args()

    fijar_semilla(a.semilla)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    xs = [json.loads(linea) for linea in a.instancias.open(encoding="utf-8")]
    train = [x for x in xs if x["particion"] == "train"]
    if a.variante == "sin_cendoj":
        train = [x for x in train if x["fuente"] == "synth"]
    train = submuestrear_docs(train, a.fraccion, a.semilla)
    evals = {p: [x for x in xs if x["particion"] == p] for p in a.eval.split(",") if p}

    tok = AutoTokenizer.from_pretrained(a.modelo)
    modelo = AutoModelForSequenceClassification.from_pretrained(a.modelo, num_labels=2).to(dev)
    dl = cargador(tok, train, a.variante, a.max_len, a.batch // a.acumular, True, a.semilla)
    pasos = math.ceil(len(dl) / a.acumular) * a.epocas
    if a.max_pasos:
        pasos = min(pasos, a.max_pasos)
    sin_decay = ["bias", "LayerNorm.weight", "layer_norm.weight"]
    grupos = [
        {"params": [p for n, p in modelo.named_parameters() if not any(s in n for s in sin_decay)], "weight_decay": 0.01},
        {"params": [p for n, p in modelo.named_parameters() if any(s in n for s in sin_decay)], "weight_decay": 0.0},
    ]
    opt = torch.optim.AdamW(grupos, lr=a.lr)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * pasos), pasos)

    t0, paso = time.time(), 0
    modelo.train()
    for _ep in range(a.epocas):
        for i, b in enumerate(dl):
            b = {k: v.to(dev) for k, v in b.items()}
            (modelo(**b).loss / a.acumular).backward()
            if (i + 1) % a.acumular == 0:
                torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
                opt.step()
                sched.step()
                opt.zero_grad(set_to_none=True)
                paso += 1
                if paso >= pasos:
                    break
        if paso >= pasos:
            break
    seg = time.time() - t0

    a.salida.mkdir(parents=True, exist_ok=True)
    nombre = f"{a.modelo.split('/')[-1]}__{a.variante}__f{a.fraccion:g}__s{a.semilla}"
    with (a.salida / f"{nombre}.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for p, ys in evals.items():
            probs = predecir(modelo, cargador(tok, ys, a.variante, a.max_len, 64, False, 0), dev)
            for x, pr in zip(ys, probs, strict=True):
                fh.write(json.dumps({"id": x["id"], "particion": p, "p": round(float(pr), 6)}) + "\n")
    meta = {"nombre": nombre, "modelo": a.modelo, "variante": a.variante, "semilla": a.semilla,
            "fraccion": a.fraccion, "n_train": len(train), "pasos": paso, "segundos": round(seg, 1),
            "dispositivo": torch.cuda.get_device_name(0) if dev == "cuda" else "cpu",
            "torch": torch.__version__, "hiper": {k: getattr(a, k) for k in ("epocas", "lr", "batch", "acumular", "max_len")}}
    (a.salida / f"{nombre}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
