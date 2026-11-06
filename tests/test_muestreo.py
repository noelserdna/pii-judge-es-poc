from src.annotate.muestreo import (
    agrupar,
    es_placeholder,
    marcar_contexto,
    muestrear,
    normalizar_span,
)


def test_normalizar_quita_tratamientos_y_puntuacion():
    assert normalizar_span("Sra. Agustina ") == "agustina"
    assert normalizar_span("El Sr. Teodosio") == "teodosio"
    assert normalizar_span("D. Juan Pérez,") == "juan pérez"
    assert normalizar_span("Dª  Carmen") == "carmen"
    assert normalizar_span("Juzgado de lo Social") == "juzgado de lo social"


def test_placeholders():
    assert es_placeholder("DIRECCION000")
    assert es_placeholder("NUM005")
    assert not es_placeholder("Valladolid")
    assert not es_placeholder("STC")


def test_agrupar_une_menciones_y_excluye_placeholders():
    cands = [
        {"doc_id": "a", "span": "Teodosio", "etiqueta": "PER"},
        {"doc_id": "a", "span": "Sr. Teodosio", "etiqueta": "PER"},
        {"doc_id": "a", "span": "Teodosio", "etiqueta": "LOC"},
        {"doc_id": "b", "span": "Teodosio", "etiqueta": "PER"},
        {"doc_id": "a", "span": "DIRECCION000", "etiqueta": "LOC"},
    ]
    g = agrupar(cands)
    assert len(g) == 3
    assert len(g[("a", "teodosio", "PER")]) == 2


def test_muestrear_respeta_cupo_y_es_reproducible():
    cands = [{"doc_id": "d", "span": f"N{i}", "etiqueta": "PER" if i % 3 else "ORG"} for i in range(50)]
    g = agrupar(cands)
    m1 = muestrear(g, max_por_doc=10, semilla=1)
    m2 = muestrear(g, max_por_doc=10, semilla=1)
    assert len(m1) == 10
    assert [x["grupo"] for x in m1] == [x["grupo"] for x in m2]
    assert {x["etiqueta"] for x in m1} == {"PER", "ORG"}


def test_marcar_contexto():
    texto = "El acusado, D. Isaac, reconoció los hechos."
    s = texto.index("Isaac")
    out = marcar_contexto(texto, s, s + 5, ventana=5)
    assert out == ", D. ⟦Isaac⟧, rec"
