"""Política de solapamiento (ADR-004).

Los candidatos que se solapan, aunque sea en un carácter, forman un bloque. De cada
bloque sale un único candidato con:
- el span del candidato **más largo** del bloque (en empate, el que empieza antes);
- la unión de detectores y de etiquetas (listas ordenadas, sin repetir);
- el score máximo.
"""

from __future__ import annotations

from .tipos import Candidato


def fusionar(candidatos: list[Candidato]) -> list[Candidato]:
    if not candidatos:
        return []
    ordenados = sorted(candidatos, key=lambda c: (c.start, -c.end))
    bloques: list[list[Candidato]] = [[ordenados[0]]]
    fin_bloque = ordenados[0].end
    for c in ordenados[1:]:
        if c.start < fin_bloque:
            bloques[-1].append(c)
            fin_bloque = max(fin_bloque, c.end)
        else:
            bloques.append([c])
            fin_bloque = c.end
    salida = []
    for b in bloques:
        base = max(b, key=lambda c: (c.longitud, -c.start))
        salida.append(
            Candidato(
                base.start,
                base.end,
                sorted({d for c in b for d in c.detector}),
                sorted({e for c in b for e in c.det_label}),
                max(c.score for c in b),
            )
        )
    return salida
