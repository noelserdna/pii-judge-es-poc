"""Prueba de humo en Colab: clona el repositorio público, construye las instancias
sintéticas y entrena 30 pasos en GPU **solo con la partición de entrenamiento**.

No sube ningún dato: todo lo que usa es público (código y corpus sintético).

Uso (desde local):  colab run --gpu T4 -s piijudge-humo tools/colab_humo.py
"""

import json
import subprocess
import sys


def sh(cmd: str) -> None:
    print(f"$ {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True)


sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv")
sh("rm -rf /content/repo && git clone -q --depth 1 https://github.com/noelserdna/pii-judge-es-poc /content/repo")
sh("pip -q install 'transformers>=4.44,<5' scikit-learn 2>&1 | tail -1")
sys.path.insert(0, "/content/repo")

from pathlib import Path  # noqa: E402

from src.data.instancias import guardar, instancias_sinteticas  # noqa: E402

xs = [x for x in instancias_sinteticas(Path("/content/repo/data/synth")) if x["particion"] == "train"]
docs = sorted({x["doc_id"] for x in xs})
for x in xs:
    if x["doc_id"] in docs[::5]:
        x["particion"] = "humo_dev"
guardar(xs, Path("/content/humo.jsonl"))
sh("cd /content/repo && python -m src.model.entrenar --instancias /content/humo.jsonl --salida /content/preds "
   "--eval humo_dev --max_pasos 30 --semilla 13 2>&1 | tail -1")
sh("cd /content/repo && python -m src.model.entrenar --instancias /content/humo.jsonl --salida /content/preds "
   "--modelo BSC-LT/RoBERTalex --eval humo_dev --max_pasos 30 --semilla 13 2>&1 | tail -1")
for f in sorted(Path("/content/preds").glob("*.meta.json")):
    m = json.loads(f.read_text())
    print("RESULTADO", m["nombre"], m["dispositivo"], m["pasos"], "pasos", m["segundos"], "s", m["torch"])
sh("pip freeze | grep -iE '^(torch|transformers|tokenizers|numpy|scikit-learn)==' ")
