"""Prueba de humo: el paquete se importa y las rutas de datos publicables existen.

Sirve para que la CI tenga al menos un test desde el primer día; los tests
reales llegan con cada paso (detector, sintéticos, particiones, métricas).
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_paquete_importable():
    import src  # noqa: F401


def test_rutas_publicables_existen():
    for ruta in ("data/synth", "data/cendoj/annot", "reports", "docs/guia"):
        assert (RAIZ / ruta).is_dir(), ruta


def test_gitignore_excluye_datos_no_publicables():
    gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    for patron in ("data/cendoj/raw/", "data/cendoj/candidates/", "checkpoints/"):
        assert patron in gitignore, patron
