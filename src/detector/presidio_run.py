"""Presidio Analyzer como **detector no visto** (solo sobre documentos de test, ADR-004)."""

from __future__ import annotations

from functools import lru_cache

from .tipos import Candidato


@lru_cache(maxsize=1)
def cargar_presidio():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    proveedor = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "es", "model_name": "es_core_news_lg"}],
        }
    )
    return AnalyzerEngine(nlp_engine=proveedor.create_engine(), supported_languages=["es"])


def detectar_presidio(texto: str, umbral: float = 0.0) -> list[Candidato]:
    motor = cargar_presidio()
    res = motor.analyze(text=texto, language="es", score_threshold=umbral)
    return [Candidato(r.start, r.end, ["presidio"], [r.entity_type], float(r.score)) for r in res]
