"""Prueba de humo de entrenamiento: ¿cabe y a qué velocidad va el afinado en esta máquina?

No usa datos reales: genera frases inventadas con un span marcado. Mide, para cada
configuración, la memoria máxima de GPU y los pasos por segundo, y al final la
inferencia en CPU. Sirve para decidir qué se entrena en local y qué en Colab.

Uso:  uv run --group ml python tools/gpu_humo.py [--modelo dccuchile/distilbert-base-spanish-uncased]
"""

import argparse
import random
import time

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

FRASES = [
    "El recurso fue interpuesto por « {x} » contra la sentencia del Juzgado de lo Social número 2.",
    "Comparece la Procuradora « {x} » en nombre y representación de la parte apelante.",
    "Los hechos ocurrieron en « {x} » durante el mes de marzo, según declaró la testigo.",
    "Se acuerda notificar la presente resolución a « {x} » con indicación de los recursos.",
]
NOMBRES = ["Eulalia", "Cuenca", "Ramiro Ortega", "Juzgado", "Victoria", "NUM000", "312/2024", "Soria"]


def lote(tok, n, max_len, dev):
    textos = [" ".join([random.choice(FRASES).format(x=random.choice(NOMBRES))] * 4) for _ in range(n)]
    enc = tok(textos, truncation=True, max_length=max_len, padding="max_length", return_tensors="pt")
    enc["labels"] = torch.randint(0, 2, (n,))
    return {k: v.to(dev) for k, v in enc.items()}


def entrenar(modelo, batch, max_len, fp16, pasos=20, grad_ckpt=False):
    dev = "cuda"
    tok = AutoTokenizer.from_pretrained(modelo)
    m = AutoModelForSequenceClassification.from_pretrained(modelo, num_labels=2).to(dev)
    if grad_ckpt:
        m.gradient_checkpointing_enable()
    opt = torch.optim.AdamW(m.parameters(), lr=3e-5)
    scaler = torch.amp.GradScaler("cuda", enabled=fp16)
    torch.cuda.reset_peak_memory_stats()
    m.train()
    t = None
    for paso in range(pasos + 3):
        if paso == 3:  # 3 pasos de calentamiento
            torch.cuda.synchronize()
            t = time.perf_counter()
        b = lote(tok, batch, max_len, dev)
        with torch.autocast("cuda", dtype=torch.float16, enabled=fp16):
            loss = m(**b).loss
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    seg = time.perf_counter() - t
    pico = torch.cuda.max_memory_allocated() / 2**20
    del m, opt
    torch.cuda.empty_cache()
    return pasos / seg, pico, batch * pasos / seg


def inferencia_cpu(modelo, max_len, n=64, batch=32):
    tok = AutoTokenizer.from_pretrained(modelo)
    m = AutoModelForSequenceClassification.from_pretrained(modelo, num_labels=2).eval()
    torch.set_num_threads(4)
    b = lote(tok, batch, max_len, "cpu")
    b.pop("labels")
    with torch.inference_mode():
        m(**b)
        t = time.perf_counter()
        for _ in range(n // batch):
            m(**b)
    return (n) / (time.perf_counter() - t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="dccuchile/distilbert-base-spanish-uncased")
    ap.add_argument("--max_len", type=int, default=192)
    a = ap.parse_args()
    random.seed(0)
    torch.manual_seed(0)
    print(f"torch {torch.__version__} · CUDA {torch.version.cuda} · {torch.cuda.get_device_name(0)}")
    print(f"modelo {a.modelo} · max_len {a.max_len}")
    configs = [(8, False, False), (8, True, False), (16, True, False), (32, True, False), (16, True, True)]
    for batch, fp16, gc in configs:
        try:
            pps, pico, eps = entrenar(a.modelo, batch, a.max_len, fp16, grad_ckpt=gc)
            print(f"batch {batch:>2} · fp16 {fp16!s:5} · grad_ckpt {gc!s:5} → {pps:5.2f} pasos/s · "
                  f"{eps:6.1f} ejemplos/s · pico GPU {pico:6.0f} MiB")
        except torch.OutOfMemoryError:
            torch.cuda.empty_cache()
            print(f"batch {batch:>2} · fp16 {fp16!s:5} · grad_ckpt {gc!s:5} → SIN MEMORIA")
    print(f"inferencia CPU (4 hilos, FP32, lotes de 32): {inferencia_cpu(a.modelo, a.max_len):.1f} ejemplos/s")


if __name__ == "__main__":
    main()
