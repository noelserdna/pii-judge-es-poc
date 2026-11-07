"""Tipos comunes del detector."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Candidato:
    """Un span que algún detector marca como posible dato personal.

    `score` es una constante heurística por regla (el detector propio no estima
    probabilidades); sirve como señal para la regresión logística, no como confianza.
    """

    start: int
    end: int
    detector: list[str] = field(default_factory=list)
    det_label: list[str] = field(default_factory=list)
    score: float = 0.0

    def solapa(self, otro: Candidato) -> bool:
        return self.start < otro.end and otro.start < self.end

    @property
    def longitud(self) -> int:
        return self.end - self.start
