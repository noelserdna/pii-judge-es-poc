"""Baselines: «aceptar todos» y regresión logística reforzada (protocolo §5).

La regresión logística ve:
- etiquetas y detectores (one-hot multietiqueta) y el score heurístico del detector;
- disparadores léxicos en la ventana izquierda («D.», «Dña.», «calle», «expediente», «Juzgado»…);
- forma de mayúsculas, longitud y presencia de dígitos del span;
- TF-IDF de n-gramas de caracteres 2–5 del span;
- bolsa de palabras de ±5 tokens de contexto.
Hiperparámetros fijos: C = 1.0, class_weight = balanced, sin búsqueda.
"""

from __future__ import annotations

import re

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer

DISPARADORES = [
    r"\bD\.\s*$", r"\bDña\.\s*$", r"\bD\.ª\s*$", r"\bSr\.?\s*$", r"\bSra\.?\s*$", r"\bcalle\s*$", r"\bC/\s*$",
    r"expediente", r"[Jj]uzgado", r"[Pp]rocurador", r"[Ll]etrad", r"[Mm]agistrad", r"\bnº", r"[Rr]ecurso",
    r"DNI", r"NIE", r"[Tt]eléfono", r"[Cc]orreo", r"[Cc]uenta", r"[Pp]onente", r"[Pp]erito", r"[Nn]otari",
]
_DISP = [re.compile(p) for p in DISPARADORES]
_TOKEN = re.compile(r"\w+", re.UNICODE)


def forma(span: str) -> list[float]:
    letras = [c for c in span if c.isalpha()]
    return [
        float(bool(span) and span[0].isupper()),
        float(bool(letras) and all(c.isupper() for c in letras)),
        float(bool(letras) and all(c.islower() for c in letras)),
        float(any(c.isdigit() for c in span)),
        min(len(span), 60) / 60,
        min(len(span.split()), 6) / 6,
    ]


def ventanas(x: dict, k: int = 5) -> str:
    izq = _TOKEN.findall(x["contexto"][: x["span_ini"]])[-k:]
    der = _TOKEN.findall(x["contexto"][x["span_fin"] :])[:k]
    return " ".join([f"I_{t.lower()}" for t in izq] + [f"D_{t.lower()}" for t in der])


def disparadores(x: dict) -> list[float]:
    izq = x["contexto"][max(0, x["span_ini"] - 60) : x["span_ini"]]
    return [float(bool(r.search(izq))) for r in _DISP]


class RegresionLogistica:
    def __init__(self, semilla: int = 0):
        self.lab = MultiLabelBinarizer()
        self.det = MultiLabelBinarizer()
        self.chars = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, lowercase=False)
        self.bow = CountVectorizer(token_pattern=r"\S+", min_df=2, binary=True)
        self.clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=3000, random_state=semilla)

    def _matriz(self, xs: list[dict], ajustar: bool):
        f = (lambda t, d: t.fit_transform(d)) if ajustar else (lambda t, d: t.transform(d))
        densas = np.array([[x["score"], *forma(x["span"]), *disparadores(x)] for x in xs])
        return sparse.hstack([
            f(self.lab, [x["det_label"] for x in xs]),
            f(self.det, [x["detector"] for x in xs]),
            sparse.csr_matrix(densas),
            f(self.chars, [x["span"] for x in xs]),
            f(self.bow, [ventanas(x) for x in xs]),
        ]).tocsr()

    def fit(self, xs: list[dict]) -> RegresionLogistica:
        self.clf.fit(self._matriz(xs, True), [x["y"] for x in xs])
        return self

    def predict_proba(self, xs: list[dict]) -> np.ndarray:
        return self.clf.predict_proba(self._matriz(xs, False))[:, 1]


def aceptar_todos(xs: list[dict]) -> np.ndarray:
    return np.ones(len(xs))
