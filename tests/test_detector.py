import importlib.util

import pytest

from src.detector.merge import fusionar
from src.detector.ner import detectar_tratamientos
from src.detector.regex_rules import detectar, dni_valido, iban_valido
from src.detector.tipos import Candidato

HAY_SPACY = importlib.util.find_spec("es_core_news_lg") is not None


def test_checksum_dni_nie():
    assert dni_valido("12345678Z")
    assert dni_valido("12345678-Z")
    assert not dni_valido("12345678A")
    assert dni_valido("X1234567L")
    assert not dni_valido("X1234567A")


def test_checksum_iban():
    assert iban_valido("ES9121000418450200051332")
    assert iban_valido("ES91 2100 0418 4502 0005 1332")
    assert not iban_valido("ES9221000418450200051332")


def test_regex_detecta_y_etiqueta():
    texto = "DNI 12345678Z, teléfono 600 123 456, correo ana@ejemplo.es, recurso 312/2024, IBAN ES9121000418450200051332."
    etiquetas = {c.det_label[0] for c in detectar(texto)}
    assert {"DNI_NIE_valido", "TELEFONO", "EMAIL", "NUM_EXPEDIENTE", "IBAN_valido"} <= etiquetas


def test_regex_marca_dni_invalido_sin_descartarlo():
    c = [x for x in detectar("con DNI 12345678A") if x.det_label[0].startswith("DNI")]
    assert c and c[0].det_label == ["DNI_NIE_invalido"]


def test_tratamientos_y_vias():
    texto = "Comparece Dña. Eulalia Martín y el Sr. Ortega, con domicilio en calle Almendro 14."
    cands = detectar_tratamientos(texto)
    spans = {texto[c.start:c.end] for c in cands}
    assert "Eulalia Martín" in spans
    assert "Ortega" in spans
    assert any(s.startswith("calle Almendro") for s in spans)


def test_fusion_conserva_el_mas_largo_y_une_detectores():
    a = Candidato(10, 16, ["spacy"], ["PER"], 0.7)
    b = Candidato(10, 22, ["tratamiento"], ["PER"], 0.8)
    c = Candidato(30, 35, ["regex"], ["NUM_EXPEDIENTE"], 0.5)
    out = fusionar([c, a, b])
    assert [(x.start, x.end) for x in out] == [(10, 22), (30, 35)]
    assert out[0].detector == ["spacy", "tratamiento"]
    assert out[0].score == 0.8


def test_fusion_encadena_solapamientos():
    out = fusionar([Candidato(0, 5, ["a"], ["X"]), Candidato(4, 9, ["b"], ["Y"]), Candidato(8, 20, ["c"], ["Z"])])
    assert len(out) == 1 and (out[0].start, out[0].end) == (8, 20)
    assert out[0].det_label == ["X", "Y", "Z"]


def test_fusion_no_une_adyacentes():
    assert len(fusionar([Candidato(0, 5, ["a"], ["X"]), Candidato(5, 9, ["b"], ["Y"])])) == 2


@pytest.mark.skipif(not HAY_SPACY, reason="modelo de spaCy no instalado (grupo detector)")
def test_ner_encuentra_persona_y_lugar():
    from src.detector.ner import detectar_ner

    texto = "La demandante, Eulalia Martín Soria, vive en Cuenca desde 2019."
    cands = detectar_ner(texto)
    etiquetas = {(texto[c.start:c.end], c.det_label[0]) for c in cands}
    assert any(lab == "PER" for _, lab in etiquetas)
    assert any(lab == "LOC" for _, lab in etiquetas)
