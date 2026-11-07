"""Chequeo de realidad (Paso 0b): detector v0 sobre 10 sentencias del CENDOJ.

Objetivo: antes de fijar los criterios del protocolo, saber cuántos candidatos
produce un detector sencillo en sentencias reales y qué tipo de falsos positivos
y de positivos aparecen. NO es el detector del Paso 2: es una versión mínima
para dimensionar.

Entrada  (local, NO se publica): data/cendoj/raw/chequeo/*.pdf y refs.csv
Salidas:
  - data/cendoj/raw/chequeo/*.txt              texto extraído (local, NO se publica)
  - data/cendoj/raw/chequeo/candidatos.csv     candidatos con contexto (local, NO se publica)
  - reports/chequeo-realidad.json              solo cifras agregadas (SÍ se publica)

Uso:  uv run --group detector python tools/chequeo_realidad.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pdfplumber
import spacy

RAIZ = Path(__file__).resolve().parents[1]
DIR = RAIZ / "data" / "cendoj" / "raw" / "chequeo"
SALIDA_PUBLICA = RAIZ / "reports" / "chequeo-realidad.json"
VENTANA = 200  # caracteres de contexto a cada lado

# --- Reglas regex v0 (sensibles a propósito: queremos falsos positivos) -------------
LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
REGEX = {
    "DNI_NIE": re.compile(r"\b[XYZ]?\d{7,8}[-\s]?[A-Z]\b"),
    "TELEFONO": re.compile(r"(?<!\d)(?:\+34\s?)?[6789]\d{2}[\s.]?\d{3}[\s.]?\d{3}(?!\d)"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "IBAN": re.compile(r"\bES\d{2}(?:[\s-]?\d{4}){5}\b"),
    # Números que "parecen" identificadores: expedientes, procedimientos, recursos...
    "NUM_EXPEDIENTE": re.compile(r"\b\d{1,6}/\d{2,4}\b"),
}
# Marcadores que el CENDOJ pone al disociar (NUM000, DIRECCION001, CALLE000, ...)
PLACEHOLDER = re.compile(r"\b[A-ZÁÉÍÓÚÑ]{3,}\d{3}\b")
# Heurística de tratamiento: "D. Xxxx", "Dña. Xxxx", "Don Xxxx"...
TRATAMIENTO = re.compile(
    r"\b(?:D\.|Dña\.|D\.ª|Dª|Don|Doña|Sr\.|Sra\.)\s+((?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s?){1,4})"
)
ROL_JUDICIAL = re.compile(
    r"(magistrad|ponente|presidente|letrad[oa] de la administraci|secretari[oa] judicial|juez|jueza)",
    re.IGNORECASE,
)
ROL_PROFESIONAL = re.compile(r"(procurador|letrad[oa]|abogad[oa]|perit[oa]|graduad[oa] social)", re.IGNORECASE)


def dni_valido(s: str) -> bool:
    s = re.sub(r"[-\s]", "", s.upper())
    num = s[:-1].replace("X", "0").replace("Y", "1").replace("Z", "2")
    return num.isdigit() and LETRAS_DNI[int(num) % 23] == s[-1]


def extraer_texto(pdf: Path) -> str:
    with pdfplumber.open(pdf) as doc:
        return "\n".join((p.extract_text() or "") for p in doc.pages)


def rol_aproximado(contexto_previo: str) -> str:
    previo = contexto_previo[-120:]
    if ROL_JUDICIAL.search(previo):
        return "judicial"
    if ROL_PROFESIONAL.search(previo):
        return "profesional"
    return "parte_u_otro"


def main() -> None:
    nlp = spacy.load("es_core_news_lg")
    nlp.max_length = 2_000_000
    refs = list(csv.DictReader((DIR / "refs.csv").open(encoding="utf-8")))
    filas: list[dict] = []
    resumen_docs = []

    for ref in refs:
        nombre = ref["roj"].replace(" ", "_").replace("/", "_")
        texto = extraer_texto(DIR / f"{nombre}.pdf")
        (DIR / f"{nombre}.txt").write_text(texto, encoding="utf-8")
        sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()

        candidatos: list[tuple[int, int, str, str]] = []  # start, end, detector, etiqueta
        for etiqueta, rx in REGEX.items():
            for m in rx.finditer(texto):
                et = etiqueta
                if etiqueta == "DNI_NIE":
                    et += "_valido" if dni_valido(m.group()) else "_invalido"
                candidatos.append((m.start(), m.end(), "regex", et))
        for m in TRATAMIENTO.finditer(texto):
            candidatos.append((m.start(1), m.end(1), "tratamiento", "PER"))
        doc = nlp(texto)
        for ent in doc.ents:
            if ent.label_ in {"PER", "LOC", "ORG"}:
                candidatos.append((ent.start_char, ent.end_char, "spacy", ent.label_))

        placeholders = Counter(re.sub(r"\d", "", m.group()) for m in PLACEHOLDER.finditer(texto))

        # Fusión mínima: mismo span exacto -> una fila con detectores combinados
        fusion: dict[tuple[int, int], dict] = {}
        for s, e, det, et in candidatos:
            clave = (s, e)
            f = fusion.setdefault(clave, {"detector": set(), "etiqueta": set()})
            f["detector"].add(det)
            f["etiqueta"].add(et)

        for (s, e), f in sorted(fusion.items()):
            span = texto[s:e]
            es_placeholder = bool(PLACEHOLDER.fullmatch(span.strip()))
            filas.append(
                {
                    "roj": ref["roj"],
                    "jurisdiccion": ref["jurisdiccion"],
                    "start": s,
                    "end": e,
                    "span": span.replace("\n", " "),
                    "detector": "+".join(sorted(f["detector"])),
                    "etiqueta": "+".join(sorted(f["etiqueta"])),
                    "placeholder": es_placeholder,
                    "rol_aprox": rol_aproximado(texto[max(0, s - VENTANA) : s]),
                    "contexto": texto[max(0, s - VENTANA) : e + VENTANA].replace("\n", " "),
                }
            )

        n_doc = [x for x in filas if x["roj"] == ref["roj"]]
        resumen_docs.append(
            {
                "roj": ref["roj"],
                "jurisdiccion": ref["jurisdiccion"],
                "organo": ref["organo"],
                "caracteres": len(texto),
                "sha256_texto": sha,
                "candidatos": len(n_doc),
                "candidatos_sin_placeholder": sum(not x["placeholder"] for x in n_doc),
                "placeholders_en_texto": dict(placeholders),
                "por_etiqueta": dict(Counter(x["etiqueta"] for x in n_doc)),
            }
        )

    with (DIR / "candidatos.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    total = Counter(x["etiqueta"] for x in filas)
    publico = {
        "descripcion": "Chequeo de realidad del Paso 0b: detector v0 sobre 10 sentencias del CENDOJ. "
        "Solo cifras agregadas; ningún texto.",
        "detector": "regex v0 + tratamiento (D./Dña.) + spaCy es_core_news_lg 3.8.0 (PER/LOC/ORG)",
        "documentos": resumen_docs,
        "totales": {
            "documentos": len(refs),
            "candidatos": len(filas),
            "candidatos_sin_placeholder": sum(not x["placeholder"] for x in filas),
            "por_etiqueta": dict(total.most_common()),
            "por_jurisdiccion": dict(Counter(x["jurisdiccion"] for x in filas)),
        },
    }
    SALIDA_PUBLICA.write_text(json.dumps(publico, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(publico["totales"], ensure_ascii=False, indent=2))
    for d in resumen_docs:
        print(d["roj"], d["jurisdiccion"], d["caracteres"], d["candidatos"], d["placeholders_en_texto"])


if __name__ == "__main__":
    main()
