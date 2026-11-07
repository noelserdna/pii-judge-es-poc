"""Detector basado en entidades nombradas (spaCy) y en una heurística de tratamientos."""

from __future__ import annotations

import re
from functools import lru_cache

from .tipos import Candidato

MODELO_SPACY = "es_core_news_lg"
ETIQUETAS_NER = {"PER", "LOC", "ORG"}
SCORE_NER = 0.7
SCORE_TRATAMIENTO = 0.8

# «D. Xxxx», «Dña. Xxxx Yyyy», «Sr. Xxxx», «calle Xxxx»…: captura las palabras con mayúscula que siguen
TRATAMIENTO = re.compile(
    r"(?:(?<=\s)|^)(?:D\.ª|Dª|Dña\.|D\.|Don|Doña|Sr\.|Sra\.|Srta\.)\s+"
    r"([A-ZÁÉÍÓÚÑ][a-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñü]+){0,3})\b"
)
VIA = re.compile(r"\b(?:[Cc]alle|C/|[Aa]venida|Avda\.|[Pp]laza|[Pp]aseo|[Cc]amino)\s+((?:[A-ZÁÉÍÓÚÑ][\wáéíóúñü]+\s?){1,4}(?:,?\s*(?:n\.?\s*º\s*)?\d+)?)")


@lru_cache(maxsize=1)
def cargar_spacy():
    import spacy

    nlp = spacy.load(MODELO_SPACY)
    nlp.max_length = 3_000_000
    return nlp


def detectar_tratamientos(texto: str) -> list[Candidato]:
    out = []
    for m in TRATAMIENTO.finditer(texto):
        ini, fin = m.start(1), m.end(1)
        while fin > ini and texto[fin - 1].isspace():
            fin -= 1
        out.append(Candidato(ini, fin, ["tratamiento"], ["PER"], SCORE_TRATAMIENTO))
    for m in VIA.finditer(texto):
        ini, fin = m.start(), m.end(1)
        while fin > ini and texto[fin - 1].isspace():
            fin -= 1
        out.append(Candidato(ini, fin, ["tratamiento"], ["DIRECCION"], SCORE_TRATAMIENTO))
    return out


def detectar_ner(texto: str) -> list[Candidato]:
    doc = cargar_spacy()(texto)
    return [
        Candidato(e.start_char, e.end_char, ["spacy"], [e.label_], SCORE_NER)
        for e in doc.ents
        if e.label_ in ETIQUETAS_NER and e.text.strip()
    ]
