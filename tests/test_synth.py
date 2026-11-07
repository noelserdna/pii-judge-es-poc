import itertools
import random

from src.data import gazetteers as g
from src.data.synth import (
    FAMILIAS,
    HUECO,
    PARTICION_FAMILIA,
    _iban,
    _nie,
    etiquetar,
    generar_documento,
    rellenar,
)
from src.detector.regex_rules import dni_valido, iban_valido


def test_listas_sin_cadenas_compartidas():
    listas = {"nombre": g.NOMBRES, "apellido": g.APELLIDOS, "municipio": g.MUNICIPIOS, "pueblo": g.PUEBLOS,
              "via": g.VIAS, "actividad": g.ACTIVIDADES}
    for (a, x), (b, y) in itertools.combinations(listas.items(), 2):
        assert not set(x) & set(y), (a, b, set(x) & set(y))


def test_gazetteers_disjuntos_por_particion():
    for nombre, parts in g.GAZ.items():
        for a, b in itertools.combinations(g.PARTICIONES, 2):
            assert not set(parts[a]) & set(parts[b]), (nombre, a, b)
        assert all(parts[p] for p in g.PARTICIONES), nombre


def test_familias_completas_por_particion():
    assert set(PARTICION_FAMILIA) == set(FAMILIAS)
    assert sorted(PARTICION_FAMILIA.values()).count("test") == 3


def test_todas_las_plantillas_tienen_huecos_validos():
    for fam in FAMILIAS.values():
        for plantilla in [fam["cab"], fam["cierre"], *fam["frases"]]:
            assert "{" not in HUECO.sub("", plantilla), plantilla  # ninguna llave suelta


def test_rellenar_registra_posiciones_exactas():
    rng = random.Random(1)
    texto, huecos = rellenar("Dña. {{NOMBRE_COMPLETO:SI:PERSONA:parte}} vive en {{MUNICIPIO:NO}}.", "train", rng)
    assert len(huecos) == 2
    for h in huecos:
        assert texto[h["start"]:h["end"]].strip() == texto[h["start"]:h["end"]]
    assert huecos[0]["etiqueta"] == "SI" and huecos[0]["rol"] == "parte"
    assert huecos[1]["etiqueta"] == "NO" and huecos[1]["categoria"] == ""


def test_valores_de_la_particion_correcta():
    rng = random.Random(2)
    for _ in range(50):
        texto, _huecos = rellenar("{{NOMBRE:SI:PERSONA:parte}}", "test", rng)
        assert texto in g.GAZ["nombre"]["test"]


def test_identificadores_validos():
    rng = random.Random(3)
    for _ in range(50):
        assert iban_valido(_iban(rng))
        assert dni_valido(_nie(rng))


def test_etiquetado_por_solape():
    doc = {"familia": "F01_desahucio", "particion": "train",
           "huecos": [{"start": 5, "end": 20, "tipo": "NOMBRE_COMPLETO", "etiqueta": "SI", "categoria": "PERSONA", "rol": "parte"},
                      {"start": 30, "end": 36, "tipo": "MUNICIPIO", "etiqueta": "NO", "categoria": "", "rol": ""}]}
    cands = [{"start": 5, "end": 12}, {"start": 30, "end": 36}, {"start": 40, "end": 45}]
    out = etiquetar(doc, cands)
    assert [c["etiqueta"] for c in out] == ["SI", "NO", "NO"]
    assert [c["fuente"] for c in out] == ["hueco", "hueco", "plantilla"]


def test_documento_reproducible():
    a = generar_documento("F03_trafico", 0, random.Random(7))
    b = generar_documento("F03_trafico", 0, random.Random(7))
    assert a == b and a["particion"] == "train"
