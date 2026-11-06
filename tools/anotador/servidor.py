"""Anotador local: una web en 127.0.0.1 para revisar y anotar instancias.

El texto de las sentencias nunca sale del ordenador: el servidor solo escucha en
127.0.0.1 y las anotaciones se guardan en un JSON local (y una copia CSV).

Modos:
  revision  la sugerencia viene rellenada; se acepta (Enter) o se cambia.
  ciego     la sugerencia se oculta hasta haber elegido una etiqueta propia;
            después se muestra para comparar. Es el modo que permite medir acuerdo (κ).

Uso (prueba en seco del Paso 1):
  uv run python tools/anotador/servidor.py \
      --entrada data/cendoj/raw/chequeo/prueba_guia_anotar.csv \
      --sugerencias data/cendoj/raw/chequeo/prueba_guia_ia.csv \
      --salida data/cendoj/raw/chequeo/prueba_guia_humano.json --modo revision
"""

from __future__ import annotations

import argparse
import csv
import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HTML = Path(__file__).with_name("index.html")
CAMPOS = ["etiqueta", "categoria", "rol", "nota"]


def leer_csv(ruta: Path) -> list[dict]:
    texto = ruta.read_text(encoding="utf-8-sig")
    sep = ";" if texto.splitlines()[0].count(";") > texto.splitlines()[0].count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=sep))


class Estado:
    def __init__(self, entrada: Path, sugerencias: Path | None, salida: Path, modo: str):
        self.items = [{"id": r["id"], "contexto": r["contexto"]} for r in leer_csv(entrada)]
        self.sug = {r["id"]: {k: r.get(k, "") for k in CAMPOS} for r in leer_csv(sugerencias)} if sugerencias else {}
        self.salida = salida
        self.modo = modo
        self.lock = threading.Lock()
        self.anot = json.loads(salida.read_text(encoding="utf-8")) if salida.exists() else {}

    def guardar(self, item_id: str, datos: dict) -> None:
        with self.lock:
            self.anot[item_id] = {**{k: datos.get(k, "") for k in CAMPOS},
                                  "acepto_sugerencia": bool(datos.get("acepto_sugerencia")),
                                  "ms": int(datos.get("ms", 0)), "modo": self.modo,
                                  "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
            self.salida.write_text(json.dumps(self.anot, ensure_ascii=False, indent=1), encoding="utf-8")
            with self.salida.with_suffix(".csv").open("w", encoding="utf-8", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["id", *CAMPOS, "acepto_sugerencia", "ms", "modo", "ts"])
                for i in self.items:
                    a = self.anot.get(i["id"])
                    if a:
                        w.writerow([i["id"], *[a[k] for k in CAMPOS], a["acepto_sugerencia"], a["ms"], a["modo"], a["ts"]])


def crear_handler(estado: Estado):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silencio en consola
            pass

        def _json(self, obj, code=200):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                data = HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif self.path == "/api/datos":
                self._json({"modo": estado.modo, "items": estado.items, "sugerencias": estado.sug,
                            "anotaciones": estado.anot})
            else:
                self._json({"error": "no encontrado"}, 404)

        def do_POST(self):
            if self.path != "/api/guardar":
                return self._json({"error": "no encontrado"}, 404)
            datos = json.loads(self.rfile.read(int(self.headers["Content-Length"])) or b"{}")
            if datos.get("id") not in {i["id"] for i in estado.items}:
                return self._json({"error": "id desconocido"}, 400)
            estado.guardar(datos["id"], datos)
            self._json({"ok": True, "hechas": len(estado.anot)})

    return Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", type=Path, required=True)
    ap.add_argument("--sugerencias", type=Path)
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--modo", choices=["revision", "ciego"], default="revision")
    ap.add_argument("--puerto", type=int, default=8765)
    a = ap.parse_args()
    estado = Estado(a.entrada, a.sugerencias, a.salida, a.modo)
    srv = ThreadingHTTPServer(("127.0.0.1", a.puerto), crear_handler(estado))
    url = f"http://127.0.0.1:{a.puerto}/"
    print(f"Anotador en {url}  ·  modo {a.modo}  ·  {len(estado.items)} instancias  ·  guardando en {a.salida}")
    print("Ctrl+C para parar.")
    webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
