"""Reglas de expresiones regulares, sensibles a propósito.

El objetivo no es acertar sino **no dejar escapar** nada: el validador se encarga
después de descartar. Por eso se aceptan DNI/NIE con letra de control incorrecta,
números con forma de expediente, teléfonos de organismos, etc.
"""

from __future__ import annotations

import re

from .tipos import Candidato

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

PATRONES: dict[str, re.Pattern] = {
    "DNI_NIE": re.compile(r"\b[XYZ]?\d{7,8}[-\s]?[A-Z]\b"),
    # sin exigir separadores: «983413482/983458513» (teléfono/fax del órgano) da dos candidatos
    "TELEFONO": re.compile(r"(?<!\d)(?:\+34\s?|0034\s?)?[6789]\d{2}[\s.]?\d{3}[\s.]?\d{3}(?!\d)"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"),
    "IBAN": re.compile(r"\bES\d{2}(?:[\s-]?\d{4}){5}\b"),
    "NUM_EXPEDIENTE": re.compile(r"\b\d{1,6}/\d{2,4}\b"),
}

SCORE = {"valido": 0.9, "invalido": 0.6, "por_defecto": 0.5}


def dni_valido(texto: str) -> bool:
    s = re.sub(r"[-\s]", "", texto.upper())
    if len(s) < 8:
        return False
    num = s[:-1].replace("X", "0").replace("Y", "1").replace("Z", "2")
    return num.isdigit() and LETRAS_DNI[int(num) % 23] == s[-1]


def iban_valido(texto: str) -> bool:
    s = re.sub(r"[\s-]", "", texto.upper())
    reordenado = s[4:] + s[:4]
    numerico = "".join(str(int(c, 36)) for c in reordenado)
    return int(numerico) % 97 == 1


def detectar(texto: str) -> list[Candidato]:
    out: list[Candidato] = []
    for etiqueta, rx in PATRONES.items():
        for m in rx.finditer(texto):
            et, score = etiqueta, SCORE["por_defecto"]
            if etiqueta == "DNI_NIE":
                ok = dni_valido(m.group())
                et, score = f"DNI_NIE_{'valido' if ok else 'invalido'}", SCORE["valido" if ok else "invalido"]
            elif etiqueta == "IBAN":
                ok = iban_valido(m.group())
                et, score = f"IBAN_{'valido' if ok else 'invalido'}", SCORE["valido" if ok else "invalido"]
            out.append(Candidato(m.start(), m.end(), ["regex"], [et], score))
    return out
