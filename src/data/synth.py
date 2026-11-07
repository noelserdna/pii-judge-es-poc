"""Generador de documentos sintéticos de estilo judicial con etiqueta conocida por construcción.

Diseño (ADR-017):
- Una **familia** es un tipo de documento (desahucio, despido, tráfico…) con su propio
  repertorio de frases. Las familias se reparten enteras entre particiones: el test usa
  estructuras de documento que el modelo no ha visto.
- Cada frase contiene **huecos** `{{TIPO:ETIQUETA:CATEGORIA:ROL}}`. El mismo tipo de dato
  aparece en contextos que se contraponen (DNI de una parte frente a número de expediente,
  teléfono personal frente al del juzgado, pueblo que identifica frente a ciudad genérica).
- Los valores salen de gazetteers **disjuntos por partición** (`gazetteers.py`).
- El texto fijo de las plantillas no contiene datos personales, así que cualquier candidato
  del detector que no se solape con un hueco es `NO` (fuente = plantilla).

Uso:  uv run --group detector python -m src.data.synth --salida data/synth
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from .gazetteers import GAZ

LETRAS = "TRWAGMYFPDXBNJZSQVHLCKE"
HUECO = re.compile(r"\{\{([A-Z_]+):(SI|NO)(?::([A-Z]*))?(?::([a-z]*))?\}\}")

# --------------------------------------------------------------------------------------
# Familias: cabecera, frases y cierre. Cada documento = cabecera + 4–6 frases + cierre.
# --------------------------------------------------------------------------------------
P = "{{NOMBRE_COMPLETO:SI:PERSONA:parte}}"
PS = "{{NOMBRE:SI:PERSONA:parte}}"
PROF = "{{NOMBRE_COMPLETO:SI:PERSONA:profesional}}"
JUD = "{{NOMBRE_COMPLETO:SI:PERSONA:judicial}}"
ORG_MUNI = "{{MUNICIPIO:NO}}"
CAB = (
    "JUZGADO DE {organo} Nº {n} DE {ORG_MUNI}\nTeléfono: {{{{TEL_ORGANO:NO}}}} · Correo: {{{{EMAIL_ORGANO:NO}}}}\n"
    "Procedimiento: {proc} {{{{EXP:NO}}}}\n"
)

FAMILIAS: dict[str, dict] = {
    "F01_desahucio": {
        "cab": CAB.format(organo="PRIMERA INSTANCIA", n=3, ORG_MUNI=ORG_MUNI, proc="Juicio verbal de desahucio"),
        "frases": [
            f"La parte actora, Dña. {P}, con DNI {{{{DNI:SI:IDENTIFICADOR:}}}}, arrendó a D. {P} la vivienda sita en {{{{VIA:SI:DIRECCION:}}}}.",
            f"Consta en autos que el arrendatario {PS} dejó de abonar la renta desde el mes de marzo.",
            "El contrato se registró con el número {{EXP:NO}} en el registro de fianzas de {{MUNICIPIO:NO}}.",
            f"La demandada fue representada por la Procuradora Sra. {PROF} y defendida por el Letrado Sr. {PROF}.",
            "Las rentas debían ingresarse en la cuenta {{IBAN:SI:IDENTIFICADOR:}} titularidad de la arrendadora.",
            "Las cantidades consignadas se depositaron en la cuenta de consignaciones del Juzgado {{IBAN_ORGANO:NO}}.",
            "La vista se celebró en la sede del Juzgado, en {{VIA_ORGANO:NO}}, sin incidencias.",
        ],
        "cierre": f"Así lo acuerda y firma el Magistrado-Juez D. {JUD}.",
    },
    "F02_despido": {
        "cab": CAB.format(organo="LO SOCIAL", n=2, ORG_MUNI=ORG_MUNI, proc="Despido"),
        "frases": [
            f"El trabajador D. {P}, con NIE {{{{NIE:SI:IDENTIFICADOR:}}}}, prestó servicios para la empresa {{{{EMPRESA:NO}}}} desde 2015.",
            f"La empresa comunicó el despido por correo electrónico a {{{{EMAIL_PERS:SI:CONTACTO:}}}}, dirección personal de {PS}.",
            f"La empresa fue representada por su administradora, Dña. {P}.",
            "El expediente de regulación se tramitó con el número {{EXP:NO}} ante la autoridad laboral de {{MUNICIPIO:NO}}.",
            f"Compareció como testigo la compañera de trabajo {P}, que confirmó el horario.",
            "Para cualquier comunicación, las partes podrán dirigirse a la oficina judicial en el teléfono {{TEL_ORGANO:NO}}.",
            f"El demandante estuvo asistido por la Graduada Social Sra. {PROF}.",
        ],
        "cierre": f"Lo pronuncia y firma la Magistrada Dña. {JUD}.",
    },
    "F03_trafico": {
        "cab": CAB.format(organo="LO PENAL", n=1, ORG_MUNI=ORG_MUNI, proc="Procedimiento abreviado"),
        "frases": [
            f"Sobre las 20:30 horas, el acusado {P}, con DNI {{{{DNI:SI:IDENTIFICADOR:}}}}, conducía el turismo por la carretera que une {{{{MUNICIPIO:NO}}}} y {{{{MUNICIPIO:NO}}}}.",
            f"El vehículo colisionó con el ciclomotor que conducía {PS}, vecino de {{{{PUEBLO:SI:OTRO:}}}}, de apenas cien habitantes.",
            "El atestado fue instruido por la Guardia Civil de {{MUNICIPIO:NO}} con el número {{EXP:NO}}.",
            f"La víctima, {P}, sufrió lesiones que tardaron en curar noventa días.",
            "El Ministerio Fiscal calificó los hechos como un delito contra la seguridad vial.",
            f"La defensa, ejercida por el Letrado {PROF}, solicitó la libre absolución.",
            "La aseguradora {{EMPRESA:NO}} consignó la indemnización en la cuenta del Juzgado {{IBAN_ORGANO:NO}}.",
        ],
        "cierre": f"Firmado: {JUD}, Magistrado.",
    },
    "F04_familia": {
        "cab": CAB.format(organo="PRIMERA INSTANCIA E INSTRUCCIÓN", n=2, ORG_MUNI=ORG_MUNI, proc="Divorcio contencioso"),
        "frases": [
            f"Dña. {P} y D. {P} contrajeron matrimonio en {{{{MUNICIPIO:NO}}}} en el año 2009.",
            "La demandante reside con los hijos en {{VIA:SI:DIRECCION:}}, domicilio familiar.",
            "El demandado podrá comunicarse con los menores a través del teléfono {{TEL_MOVIL:SI:CONTACTO:}}.",
            "La pensión de alimentos se ingresará en la cuenta {{IBAN:SI:IDENTIFICADOR:}} dentro de los cinco primeros días de cada mes.",
            "El informe del equipo psicosocial del Juzgado de {{MUNICIPIO:NO}} se incorporó al expediente {{EXP:NO}}.",
            f"Actuó como perito la psicóloga Sra. {PROF}.",
        ],
        "cierre": f"Así lo manda y firma la Magistrada-Jueza Dña. {JUD}.",
    },
    "F05_honor": {
        "cab": CAB.format(organo="PRIMERA INSTANCIA", n=5, ORG_MUNI=ORG_MUNI, proc="Juicio ordinario"),
        "frases": [
            f"La actora, Dña. {P}, fue incluida en el fichero de morosos a instancia de la entidad {{{{EMPRESA:NO}}}}.",
            "La comunicación previa se envió a {{EMAIL_PERS:SI:CONTACTO:}}, cuenta que la actora no utilizaba.",
            "La entidad alegó que la deuda derivaba del contrato número {{EXP:NO}}.",
            "La única {{ACTIVIDAD:SI:OTRO:}} de {{PUEBLO:SI:OTRO:}} declaró haber sido rechazada por varios bancos.",
            "La ciudad de {{MUNICIPIO:NO}} cuenta con varias oficinas de la entidad demandada.",
            f"La demandada estuvo representada por el Procurador D. {PROF}.",
        ],
        "cierre": f"Es ponente el Ilmo. Sr. {JUD}.",
    },
    "F06_herencia": {
        "cab": CAB.format(organo="PRIMERA INSTANCIA", n=7, ORG_MUNI=ORG_MUNI, proc="Juicio ordinario"),
        "frases": [
            f"El causante, D. {P}, otorgó testamento ante el Notario de {{{{MUNICIPIO:NO}}}} D. {PROF}.",
            f"En él desheredó a su hija {PS}, alegando maltrato de obra.",
            f"La heredera {P}, con DNI {{{{DNI:SI:IDENTIFICADOR:}}}}, se opuso a la partición.",
            "La finca está inscrita en el Registro de la Propiedad de {{MUNICIPIO:NO}} con el número {{EXP:NO}}.",
            f"El causante vivió sus últimos años en {{{{VIA:SI:DIRECCION:}}}}, con su cuidadora {P}.",
            "La sociedad familiar {{EMPRESA:NO}} gestionaba las explotaciones agrícolas.",
        ],
        "cierre": f"Firma la sentencia el Magistrado D. {JUD}.",
    },
    "F07_contencioso": {
        "cab": CAB.format(organo="LO CONTENCIOSO-ADMINISTRATIVO", n=1, ORG_MUNI=ORG_MUNI, proc="Procedimiento abreviado"),
        "frases": [
            f"El recurrente, D. {P}, impugna la sanción impuesta por el Ayuntamiento de {{{{MUNICIPIO:NO}}}}.",
            "La resolución sancionadora se dictó en el expediente {{EXP:NO}} por infracción de la ordenanza municipal.",
            "El recurrente designó como domicilio a efectos de notificaciones {{VIA:SI:DIRECCION:}}.",
            "El Ayuntamiento atiende al público en {{VIA_ORGANO:NO}} y en el teléfono {{TEL_ORGANO:NO}}.",
            f"La Administración estuvo representada por el Letrado consistorial Sr. {PROF}.",
            "El recurrente facilitó el teléfono {{TEL_MOVIL:SI:CONTACTO:}} para notificaciones.",
        ],
        "cierre": f"Lo acuerda y firma la Magistrada Dña. {JUD}.",
    },
    "F08_lesiones": {
        "cab": CAB.format(organo="INSTRUCCIÓN", n=4, ORG_MUNI=ORG_MUNI, proc="Diligencias previas"),
        "frases": [
            f"El día de los hechos, {P} golpeó a {P} en la terraza de un bar de {{{{MUNICIPIO:NO}}}}.",
            "La víctima, que trabaja como {{ACTIVIDAD:SI:OTRO:}} en {{PUEBLO:SI:OTRO:}}, fue atendida en el centro de salud.",
            "El parte de lesiones se registró con el número {{EXP:NO}}.",
            "El investigado, con DNI {{DNI:SI:IDENTIFICADOR:}}, se acogió a su derecho a no declarar.",
            f"Asistió al investigado la Letrada de oficio Dña. {PROF}.",
            "Las actuaciones se remitieron al Juzgado de lo Penal de {{MUNICIPIO:NO}}.",
        ],
        "cierre": f"Lo manda y firma el Juez D. {JUD}.",
    },
    "F09_reclamacion": {
        "cab": CAB.format(organo="PRIMERA INSTANCIA", n=1, ORG_MUNI=ORG_MUNI, proc="Monitorio"),
        "frases": [
            f"La entidad {{{{EMPRESA:NO}}}} reclama a D. {P} la cantidad de 4.250 euros.",
            "El deudor, con NIE {{NIE:SI:IDENTIFICADOR:}}, fue requerido en {{VIA:SI:DIRECCION:}}.",
            "El requerimiento se practicó por el Servicio Común de Notificaciones de {{MUNICIPIO:NO}}.",
            "El deudor indicó como contacto el correo {{EMAIL_PERS:SI:CONTACTO:}}.",
            "La cantidad reclamada deberá ingresarse en la cuenta del Juzgado {{IBAN_ORGANO:NO}} con referencia {{EXP:NO}}.",
            f"La entidad actuó representada por la Procuradora Dña. {PROF}.",
        ],
        "cierre": f"Lo acuerda la Letrada de la Administración de Justicia Dña. {JUD}.",
    },
    "F10_menores": {
        "cab": CAB.format(organo="MENORES", n=1, ORG_MUNI=ORG_MUNI, proc="Expediente de reforma"),
        "frases": [
            f"El menor {PS}, de dieciséis años, residente en {{{{VIA:SI:DIRECCION:}}}}, está acusado de un delito de daños.",
            f"Su madre, Dña. {P}, con DNI {{{{DNI:SI:IDENTIFICADOR:}}}}, compareció como responsable civil.",
            "Los daños se causaron en el polideportivo municipal de {{MUNICIPIO:NO}}.",
            "El equipo técnico informó favorablemente; contacto de la familia: {{TEL_MOVIL:SI:CONTACTO:}}.",
            "La Fiscalía de Menores de {{MUNICIPIO:NO}} solicitó una medida de libertad vigilada en el expediente {{EXP:NO}}.",
            f"Defendió al menor el Letrado D. {PROF}.",
        ],
        "cierre": f"Firmado: {JUD}, Juez de Menores.",
    },
    "F11_seguros": {
        "cab": CAB.format(organo="PRIMERA INSTANCIA", n=9, ORG_MUNI=ORG_MUNI, proc="Juicio ordinario"),
        "frases": [
            f"El asegurado, D. {P}, sufrió un incendio en la nave que su empresa {{{{EMPRESA:NO}}}} ocupaba en el polígono de {{{{MUNICIPIO:NO}}}}.",
            f"El perito de la aseguradora, Sr. {PROF}, cifró los daños en 180.000 euros.",
            "La póliza se suscribió con el número {{EXP:NO}}.",
            "El asegurado vivía en {{VIA:SI:DIRECCION:}}, a escasos metros de la nave.",
            "La aseguradora tiene su domicilio social en {{VIA_ORGANO:NO}}.",
            f"Declaró como testigo el vigilante {P}, con teléfono {{{{TEL_MOVIL:SI:CONTACTO:}}}}.",
        ],
        "cierre": f"Es ponente la Ilma. Sra. Dña. {JUD}.",
    },
    "F12_extranjeria": {
        "cab": CAB.format(organo="LO CONTENCIOSO-ADMINISTRATIVO", n=2, ORG_MUNI=ORG_MUNI, proc="Recurso de apelación"),
        "frases": [
            f"El recurrente, D. {P}, con NIE {{{{NIE:SI:IDENTIFICADOR:}}}}, solicitó autorización de residencia por arraigo.",
            "La Subdelegación del Gobierno en {{MUNICIPIO:NO}} denegó la solicitud en el expediente {{EXP:NO}}.",
            "El recurrente trabaja como {{ACTIVIDAD:SI:OTRO:}} en {{PUEBLO:SI:OTRO:}}, donde es el único vecino extranjero.",
            f"Aportó un contrato firmado con su empleadora, Dña. {P}.",
            "La oficina de extranjería atiende en {{VIA_ORGANO:NO}} y en el teléfono {{TEL_ORGANO:NO}}.",
            f"Estuvo asistido por la Abogada Dña. {PROF}.",
        ],
        "cierre": f"Así lo pronuncian y firman los Magistrados {JUD} y {JUD}.",
    },
}

# Concordancia de género: «Dña./Sra.» + nombre femenino; «D./Sr.» + nombre masculino.
_FEM = re.compile(r"((?:Dña\.|Sra\.)\s+)\{\{(NOMBRE(?:_COMPLETO)?):")
_MASC = re.compile(r"((?<!\w)(?:D\.|Sr\.)\s+)\{\{(NOMBRE(?:_COMPLETO)?):")


def _concordar(t: str) -> str:
    return _MASC.sub(r"\1{{\2_M:", _FEM.sub(r"\1{{\2_F:", t))


for _fam in FAMILIAS.values():
    _fam["cab"], _fam["cierre"] = _concordar(_fam["cab"]), _concordar(_fam["cierre"])
    _fam["frases"] = [_concordar(f) for f in _fam["frases"]]

PARTICION_FAMILIA = {
    **{f: "train" for f in ("F01_desahucio", "F02_despido", "F03_trafico", "F04_familia", "F05_honor", "F06_herencia", "F07_contencioso")},
    **{f: "cal" for f in ("F08_lesiones", "F09_reclamacion")},
    **{f: "test" for f in ("F10_menores", "F11_seguros", "F12_extranjeria")},
}
MIN_POSITIVOS = {"train": 1000, "cal": 320, "test": 480}


# --------------------------------------------------------------------------------------
# Generadores de valores
# --------------------------------------------------------------------------------------
def _dni(rng: random.Random, valido: bool = True) -> str:
    n = rng.randint(10_000_000, 99_999_999)
    letra = LETRAS[n % 23] if valido else LETRAS[(n + rng.randint(1, 22)) % 23]
    return f"{n}{letra}"


def _nie(rng: random.Random) -> str:
    pref = rng.choice("XYZ")
    n = rng.randint(1_000_000, 9_999_999)
    letra = LETRAS[int(f"{'XYZ'.index(pref)}{n}") % 23]
    return f"{pref}{n}{letra}"


def _iban(rng: random.Random) -> str:
    bban = "".join(str(rng.randint(0, 9)) for _ in range(20))
    num = int(bban + "142800")  # E=14, S=28, 00
    dc = 98 - num % 97
    s = f"ES{dc:02d}{bban}"
    return " ".join(s[i : i + 4] for i in range(0, 24, 4))


def valor(tipo: str, part: str, rng: random.Random) -> str:
    g = {k: v[part] for k, v in GAZ.items()}
    lista = {"F": g["nombre_f"], "M": g["nombre_m"]}.get(tipo[-1] if tipo.endswith(("_F", "_M")) else "", g["nombre"])
    nombre, ap1, ap2 = rng.choice(lista), rng.choice(g["apellido"]), rng.choice(g["apellido"])
    match tipo.removesuffix("_F").removesuffix("_M"):
        case "NOMBRE_COMPLETO":
            return f"{nombre} {ap1} {ap2}"
        case "NOMBRE":
            return nombre
        case "MUNICIPIO":
            return rng.choice(g["municipio"])
        case "PUEBLO":
            return rng.choice(g["pueblo"])
        case "ACTIVIDAD":
            return rng.choice(g["actividad"])
        case "VIA":
            return f"calle {rng.choice(g['via'])} {rng.randint(1, 120)}, {rng.randint(1, 6)}º {rng.choice('ABCD')}"
        case "VIA_ORGANO":
            return f"calle {rng.choice(g['via'])} {rng.randint(1, 40)}, planta baja"
        case "DNI":
            return _dni(rng, valido=rng.random() > 0.15)  # 15 % con letra errónea, como en la vida real
        case "NIE":
            return _nie(rng)
        case "EXP":
            return f"{rng.randint(1, 2400)}/{rng.choice([2021, 2022, 2023, 2024, 2025])}"
        case "TEL_MOVIL":
            return f"6{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}"
        case "TEL_ORGANO":
            return f"9{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}"
        case "EMAIL_PERS":
            dom = rng.choice(["correo.es", "buzon.net", "mimail.com"])
            return f"{nombre.lower()}.{ap1.lower()}{rng.randint(1, 99)}@{dom}"
        case "EMAIL_ORGANO":
            return f"juzgado{rng.randint(1, 9)}.{rng.choice(g['municipio']).lower()}@justicia.es"
        case "IBAN" | "IBAN_ORGANO":
            return _iban(rng)
        case "EMPRESA":
            return f"{rng.choice([ap1 + ' e Hijos', 'Hermanos ' + ap1, ap1 + ' y ' + ap2])} {rng.choice(['S.L.', 'S.A.'])}"
    raise ValueError(tipo)


def rellenar(plantilla: str, part: str, rng: random.Random) -> tuple[str, list[dict]]:
    """Sustituye los huecos y devuelve el texto y la lista de huecos con sus posiciones."""
    salida, huecos, pos = [], [], 0
    for m in HUECO.finditer(plantilla):
        salida.append(plantilla[pos : m.start()])
        ini = sum(len(x) for x in salida)
        v = valor(m.group(1), part, rng)
        salida.append(v)
        huecos.append({"start": ini, "end": ini + len(v), "tipo": m.group(1), "etiqueta": m.group(2),
                       "categoria": m.group(3) or "", "rol": m.group(4) or ""})
        pos = m.end()
    salida.append(plantilla[pos:])
    return "".join(salida), huecos


def generar_documento(familia: str, idx: int, rng: random.Random) -> dict:
    fam = FAMILIAS[familia]
    part = PARTICION_FAMILIA[familia]
    frases = rng.sample(fam["frases"], k=min(len(fam["frases"]), rng.randint(4, 6)))
    plantilla = fam["cab"] + "\n" + "\n".join(frases) + "\n" + fam["cierre"]
    texto, huecos = rellenar(plantilla, part, rng)
    return {"doc_id": f"{familia}_{idx:04d}", "familia": familia, "particion": part, "texto": texto, "huecos": huecos}


def etiquetar(doc: dict, cands: list[dict]) -> list[dict]:
    """Etiqueta cada candidato con el hueco con el que se solapa (si alguno es SI, gana SI)."""
    out = []
    for c in cands:
        solapes = [h for h in doc["huecos"] if c["start"] < h["end"] and h["start"] < c["end"]]
        si = [h for h in solapes if h["etiqueta"] == "SI"]
        h = si[0] if si else (solapes[0] if solapes else None)
        out.append({**c, "familia": doc["familia"], "particion": doc["particion"],
                    "etiqueta": h["etiqueta"] if h else "NO", "categoria": h["categoria"] if h else "",
                    "rol": h["rol"] if h else "", "tipo_hueco": h["tipo"] if h else "",
                    "fuente": "hueco" if h else "plantilla"})
    return out


def main() -> None:
    from src.detector.run import detectar_documento

    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=Path("data/synth"))
    ap.add_argument("--semilla", type=int, default=20261107)
    a = ap.parse_args()
    rng = random.Random(a.semilla)
    a.salida.mkdir(parents=True, exist_ok=True)
    docs, cands = [], []
    for part, minimo in MIN_POSITIVOS.items():
        familias = sorted(f for f, p in PARTICION_FAMILIA.items() if p == part)
        positivos, i = 0, 0
        while positivos < minimo:
            fam = familias[i % len(familias)]
            d = generar_documento(fam, i // len(familias), rng)
            cs = etiquetar(d, detectar_documento(d["doc_id"], d["texto"]))
            docs.append(d)
            cands.extend(cs)
            positivos += sum(c["etiqueta"] == "SI" for c in cs)
            i += 1
    with (a.salida / "documentos.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for d in docs:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    with (a.salida / "candidatos.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for c in cands:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    # recall del detector sobre los huecos SI (cuántos datos personales «ve»)
    vistos = {(c["doc_id"], c["start"], c["end"]) for c in cands}
    huecos_si = [(d["doc_id"], h) for d in docs for h in d["huecos"] if h["etiqueta"] == "SI"]
    detectados = sum(any(c["doc_id"] == did and c["start"] < h["end"] and h["start"] < c["end"]
                         for c in cands if c["doc_id"] == did) for did, h in huecos_si)
    resumen = {
        "semilla": a.semilla,
        "documentos": dict(Counter(d["particion"] for d in docs)),
        "candidatos": dict(Counter(c["particion"] for c in cands)),
        "positivos": dict(Counter(c["particion"] for c in cands if c["etiqueta"] == "SI")),
        "por_fuente": dict(Counter(c["fuente"] for c in cands)),
        "por_categoria_positivos": dict(Counter(c["categoria"] for c in cands if c["etiqueta"] == "SI")),
        "huecos_si": len(huecos_si),
        "huecos_si_detectados": detectados,
        "recall_detector_sobre_huecos_si": round(detectados / len(huecos_si), 4),
        "candidatos_unicos": len(vistos),
    }
    (a.salida / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
