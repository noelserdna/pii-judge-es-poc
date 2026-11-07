"""Agrupación y muestreo de candidatos para anotar (ADR-012).

- Grupo = (documento, forma normalizada del span, etiqueta del detector).
- Instancia = una mención de cada grupo, elegida al azar con semilla fija.
- Muestreo por documento: hasta N grupos, estratificados por etiqueta del detector.
"""

from __future__ import annotations

import random
import re
from collections import defaultdict
from collections.abc import Iterable

TRATAMIENTOS = re.compile(
    r"^(?:(?:el|la)\s+)?(?:srta\.?|sra\.?|sr\.?|d\.ª|dª|dña\.?|doña|don|d/ña:?|d\.)\s*",
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(r"^[A-ZÁÉÍÓÚÑ]{3,}\d{3}$")
MARCA_INI, MARCA_FIN = "⟦", "⟧"


def normalizar_span(span: str) -> str:
    """Minúsculas, sin tratamientos iniciales, sin puntuación ni espacios en los extremos."""
    s = " ".join(span.split()).strip()
    s = TRATAMIENTOS.sub("", s)
    return s.lower().strip(" .,;:()\"'«»")


def es_placeholder(span: str) -> bool:
    return bool(PLACEHOLDER.match(span.strip()))


def clave_grupo(c: dict) -> tuple[str, str, str]:
    return (c["doc_id"], normalizar_span(c["span"]), c["etiqueta"])


def agrupar(candidatos: Iterable[dict]) -> dict[tuple[str, str, str], list[dict]]:
    grupos: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for c in candidatos:
        if es_placeholder(c["span"]) or not normalizar_span(c["span"]):
            continue
        grupos[clave_grupo(c)].append(c)
    return dict(grupos)


def muestrear(
    grupos: dict[tuple[str, str, str], list[dict]], max_por_doc: int, semilla: int
) -> list[dict]:
    """Devuelve una instancia por grupo muestreado: hasta `max_por_doc` grupos por documento,
    repartidos entre etiquetas del detector de forma proporcional (mínimo 1 por etiqueta)."""
    rng = random.Random(semilla)
    por_doc: dict[str, dict[str, list[tuple]]] = defaultdict(lambda: defaultdict(list))
    for clave in sorted(grupos):
        por_doc[clave[0]][clave[2]].append(clave)

    instancias = []
    for doc in sorted(por_doc):
        estratos = por_doc[doc]
        total = sum(len(v) for v in estratos.values())
        cupo = min(max_por_doc, total)
        # reparto proporcional con mínimo 1 por estrato, ajustado al cupo
        asign = {e: max(1, round(cupo * len(v) / total)) for e, v in estratos.items()}
        while sum(asign.values()) > cupo:
            e = max(asign, key=lambda k: asign[k])
            asign[e] -= 1
        for e in sorted(estratos):
            claves = estratos[e][:]
            rng.shuffle(claves)
            for clave in claves[: min(asign[e], len(claves))]:
                mencion = rng.choice(grupos[clave])
                instancias.append({**mencion, "grupo": "|".join(clave), "n_menciones": len(grupos[clave])})
    return instancias


def marcar_contexto(texto: str, start: int, end: int, ventana: int = 200) -> str:
    """Fragmento de ±ventana caracteres con el span marcado entre ⟦ ⟧, en una sola línea."""
    a, b = max(0, start - ventana), min(len(texto), end + ventana)
    frag = texto[a:start] + MARCA_INI + texto[start:end] + MARCA_FIN + texto[end:b]
    return " ".join(frag.split())
