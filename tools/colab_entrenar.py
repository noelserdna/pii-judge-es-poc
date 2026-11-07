"""Orquesta todas las corridas del protocolo en Google Colab con la CLI `colab` (ADR-016).

Pasos: crea una sesión con GPU → clona el repositorio público → sube el fichero de
instancias (único dato que sale del ordenador) → ejecuta cada configuración → descarga
las predicciones → **libera siempre la sesión** (también si algo falla).

Configuraciones del protocolo (§5 y §9):
- DistilBETO completa ×3 semillas            (candidato, criterios C1–C3)
- DistilBETO sin_mayuscula, solo_candidato, solo_contexto, sin_cendoj ×3 (ablaciones)
- DistilBETO completa fracción 0,25 y 0,5 ×3 (curva de aprendizaje)
- RoBERTalex completa ×3                     (techo)

Uso:
  uv run python tools/colab_entrenar.py --instancias inst.jsonl --salida reports/predicciones [--solo-humo]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = "https://github.com/noelserdna/pii-judge-es-poc"
SEMILLAS = (13, 42, 2026)
DISTIL = "dccuchile/distilbert-base-spanish-uncased"
ROBERTA = "BSC-LT/RoBERTalex"


def configuraciones(humo: bool) -> list[dict]:
    if humo:
        return [{"modelo": DISTIL, "variante": "completa", "fraccion": 1.0, "semilla": 13, "max_pasos": 20}]
    cs = [{"modelo": DISTIL, "variante": "completa", "fraccion": 1.0, "semilla": s} for s in SEMILLAS]
    for v in ("sin_mayuscula", "solo_candidato", "solo_contexto", "sin_cendoj"):
        cs += [{"modelo": DISTIL, "variante": v, "fraccion": 1.0, "semilla": s} for s in SEMILLAS]
    for f in (0.25, 0.5):
        cs += [{"modelo": DISTIL, "variante": "completa", "fraccion": f, "semilla": s} for s in SEMILLAS]
    cs += [{"modelo": ROBERTA, "variante": "completa", "fraccion": 1.0, "semilla": s} for s in SEMILLAS]
    return cs


def colab(*args: str, entrada: str | None = None, timeout: float | None = None) -> str:
    r = subprocess.run(["colab", *args], input=entrada, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"colab {' '.join(args)} falló:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instancias", type=Path, required=True)
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--sesion", default="piijudge")
    ap.add_argument("--gpu", default="T4")
    ap.add_argument("--eval", default="cal,test,test_presidio")
    ap.add_argument("--solo-humo", action="store_true")
    a = ap.parse_args()
    a.salida.mkdir(parents=True, exist_ok=True)
    s = a.sesion
    print(f"[orquestador] creando sesión {s} con {a.gpu}…", flush=True)
    colab("new", "-s", s, "--gpu", a.gpu)
    try:
        colab("exec", "-s", s, "--timeout", "600", entrada=(
            "import subprocess\n"
            f"subprocess.run('rm -rf /content/repo && git clone -q --depth 1 {REPO} /content/repo', shell=True, check=True)\n"
            "subprocess.run('pip -q install \"transformers>=4.44,<5\" scikit-learn', shell=True, check=True)\n"
            "print(subprocess.run('nvidia-smi --query-gpu=name --format=csv,noheader', shell=True, capture_output=True, text=True).stdout)\n"
        ))
        colab("upload", "-s", s, str(a.instancias), "/content/instancias.jsonl")
        metas = []
        for c in configuraciones(a.solo_humo):
            t0 = time.time()
            extra = f" --max_pasos {c['max_pasos']}" if c.get("max_pasos") else ""
            cmd = (f"cd /content/repo && python -m src.model.entrenar --instancias /content/instancias.jsonl "
                   f"--salida /content/preds --modelo {c['modelo']} --variante {c['variante']} "
                   f"--fraccion {c['fraccion']} --semilla {c['semilla']} --eval {a.eval}{extra} 2>&1 | tail -1")
            out = colab("exec", "-s", s, "--timeout", "3600", entrada=(
                f"import subprocess\nr = subprocess.run({cmd!r}, shell=True, capture_output=True, text=True)\n"
                "print(r.stdout[-3000:])\n"))
            linea = [x for x in out.splitlines() if x.startswith("{")]
            meta = json.loads(linea[-1]) if linea else {"error": out[-500:]}
            metas.append(meta)
            print(f"[orquestador] {meta.get('nombre', c)} · {time.time() - t0:.0f} s", flush=True)
            nombre = meta.get("nombre")
            if nombre:
                colab("download", "-s", s, f"/content/preds/{nombre}.jsonl", str(a.salida / f"{nombre}.jsonl"))
                (a.salida / f"{nombre}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                                                               encoding="utf-8", newline="\n")
        entorno = colab("exec", "-s", s, entrada=(
            "import subprocess\nprint(subprocess.run(\"nvidia-smi --query-gpu=name,driver_version --format=csv,noheader; "
            "python -V; pip freeze | grep -iE '^(torch|transformers|tokenizers|numpy|scikit-learn|safetensors)'\", "
            "shell=True, capture_output=True, text=True).stdout)\n"))
        (a.salida.parent / "entorno-colab.txt").write_text(entorno, encoding="utf-8", newline="\n")
        print(json.dumps({"corridas": len(metas), "errores": sum("error" in m for m in metas)}, ensure_ascii=False))
    finally:
        print(f"[orquestador] liberando sesión {s}", flush=True)
        try:
            colab("stop", "-s", s)
        except Exception as e:  # noqa: BLE001
            print(f"[orquestador] AVISO: no se pudo parar la sesión: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
