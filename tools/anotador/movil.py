"""Anotador para el móvil, sin servidor y sin conexión.

  exportar  genera UN fichero HTML con las instancias dentro. Se copia al teléfono (por cable)
            y se abre en el navegador. Funciona sin internet y guarda en el propio teléfono
            (localStorage). Ningún dato pasa por un servidor ni por un servicio externo.
  importar  fusiona el JSON que exporta el teléfono con la anotación del ordenador.

Uso:
  uv run python tools/anotador/movil.py exportar \
      --entrada data/cendoj/raw/conjunto/anotar.csv \
      --anot data/cendoj/raw/conjunto/anotacion_humano.json \
      --salida data/cendoj/raw/conjunto/anotador_movil.html
  uv run python tools/anotador/movil.py importar \
      --movil anotaciones_movil.json --anot data/cendoj/raw/conjunto/anotacion_humano.json

El HTML contiene texto del CENDOJ: se queda en data/cendoj/raw/ (no versionado) y solo se copia
a un dispositivo propio. No enviarlo por mensajería, correo ni nubes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from servidor import leer_csv  # noqa: E402

HTML = Path(__file__).with_name("index.html")

# Sustituye las llamadas al servidor por el almacenamiento del navegador.
SHIM = r"""
<script>
const DATOS = __DATOS__;
const CLAVE = 'pii-judge-anot-' + DATOS.huella;
function leerLS(){ try { return JSON.parse(localStorage.getItem(CLAVE) || '{}') } catch(e) { return {} } }
function escribirLS(o){ try { localStorage.setItem(CLAVE, JSON.stringify(o)); return true } catch(e) { return false } }
const respuesta = o => Promise.resolve({ json: () => Promise.resolve(o) });
window.fetch = (url, opt) => {
  if (url.startsWith('/api/datos')) {
    const anot = Object.assign({}, DATOS.anotaciones, leerLS());
    return respuesta({ modo: DATOS.modo, items: DATOS.items, sugerencias: {}, anotaciones: anot });
  }
  if (url.startsWith('/api/guardar')) {
    const d = JSON.parse(opt.body), o = leerLS();
    o[d.id] = { etiqueta: d.etiqueta || '', categoria: d.categoria || '', rol: d.rol || '', nota: d.nota || '',
      acepto_sugerencia: false, etiqueta_inicial: d.etiqueta_inicial || '', ms: Math.round(d.ms || 0),
      modo: DATOS.modo, ts: new Date().toISOString().slice(0, 19), dispositivo: 'movil' };
    const ok = escribirLS(o);
    if (!ok) alert('No se pudo guardar en el teléfono. Exporta ya lo hecho.');
    return respuesta({ ok, hechas: Object.keys(o).length });
  }
  return respuesta({ error: 'no encontrado' });
};
function exportar(){
  const o = leerLS(), n = Object.keys(o).length;
  const blob = new Blob([JSON.stringify(o, null, 1)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'anotaciones_movil_' + new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-') + '.json';
  document.body.appendChild(a); a.click(); a.remove();
  document.getElementById('nexp').textContent = n + ' exportadas';
}
</script>
"""

BARRA = """<div style="max-width:980px;margin:0 auto;padding:6px 16px;display:flex;gap:10px;align-items:center;font-size:13px">
  <button onclick="exportar()" style="padding:8px 14px;border-radius:9px;border:1px solid var(--ac);background:var(--card);color:var(--ac);font-weight:650">Exportar</button>
  <span id="nexp" style="color:var(--mut)">Se guarda en el teléfono. Exporta de vez en cuando.</span>
</div></header>"""


def exportar(a) -> None:
    items = [{"id": r["id"], "contexto": r["contexto"]} for r in leer_csv(a.entrada)]
    anot = json.loads(a.anot.read_text(encoding="utf-8")) if a.anot and a.anot.exists() else {}
    huella = hashlib.sha256("|".join(i["id"] for i in items).encode()).hexdigest()[:12]
    datos = {"modo": "ciego", "items": items, "anotaciones": anot, "huella": huella}
    html = HTML.read_text(encoding="utf-8")
    for viejo, nuevo in [("<script>\nconst $=", SHIM.replace("__DATOS__", json.dumps(datos, ensure_ascii=False)
                                                              .replace("</", "<\\/")) + "<script>\nconst $="),
                         ("</div></header>", BARRA)]:
        assert html.count(viejo) == 1, viejo
        html = html.replace(viejo, nuevo)
    a.salida.write_text(html, encoding="utf-8", newline="\n")
    print(f"{a.salida}  ·  {len(items)} instancias  ·  {len(anot)} ya anotadas  ·  {a.salida.stat().st_size / 1e6:.2f} MB")


def importar(a) -> None:
    ids = None
    if a.entrada:
        ids = {r["id"] for r in leer_csv(a.entrada)}
    actual = json.loads(a.anot.read_text(encoding="utf-8")) if a.anot.exists() else {}
    nuevas = 0
    for f in a.movil:
        for k, v in json.loads(Path(f).read_text(encoding="utf-8")).items():
            if ids is not None and k not in ids:
                sys.exit(f"id desconocido en {f}: {k}")
            if not v.get("etiqueta"):
                continue
            if k not in actual or v.get("ts", "") > actual[k].get("ts", ""):
                nuevas += k not in actual
                actual[k] = v
    a.anot.write_text(json.dumps(actual, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.anot}: {len(actual)} anotadas ({nuevas} nuevas desde el móvil)")


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("exportar")
    e.add_argument("--entrada", type=Path, required=True)
    e.add_argument("--anot", type=Path)
    e.add_argument("--salida", type=Path, required=True)
    i = sp.add_parser("importar")
    i.add_argument("--movil", nargs="+", required=True)
    i.add_argument("--anot", type=Path, required=True)
    i.add_argument("--entrada", type=Path, help="CSV de instancias, para rechazar ids desconocidos")
    a = ap.parse_args()
    exportar(a) if a.cmd == "exportar" else importar(a)


if __name__ == "__main__":
    main()
