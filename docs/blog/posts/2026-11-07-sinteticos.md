---
date: 2026-11-07
categories:
  - Paso 3
  - Datos
---

# Paso 3b · Un corpus sintético de 313 documentos, y por qué la concordancia de género importa

Hay ya un corpus sintético completo: 12 tipos de documento judicial inventados, con los datos personales insertados en posiciones conocidas, de modo que la etiqueta sale gratis y es exacta. Los mínimos de positivos del protocolo se cumplen. La lección del día está en los detalles que delatan que un texto es sintético.

<!-- more -->

## Qué se hizo

- **`src/data/synth.py`**: el generador, con 12 familias, huecos tipados y etiquetado por solapamiento con los candidatos del detector.
- **`src/data/gazetteers.py`**: las listas de nombres (separados por género), apellidos, municipios, pueblos, vías y oficios, repartidas 60/20/20 sin cadenas compartidas.
- **9 tests nuevos**: listas disjuntas, plantillas sin llaves sueltas, posiciones exactas, IBAN y NIE válidos, reproducibilidad.
- **Corpus publicado** en [`data/synth/`](https://github.com/noelserdna/pii-judge-es-poc/tree/main/data/synth) con licencia CC BY 4.0 y un fichero de [fuentes](https://github.com/noelserdna/pii-judge-es-poc/blob/main/data/synth/FUENTES.md).
- **[ADR-017](../../decisiones/ADR-017-sinteticos.md)**: el diseño completo del corpus.

## Cifras

| Partición | Familias | Documentos | Candidatos | Positivos | Mínimo del protocolo |
|---|---|---|---|---|---|
| Entrenamiento | 7 | 173 | 2.559 | 1.003 | — |
| Calibración | 2 | 60 | 775 | **322** | ≥ 300 ✔ |
| Test | 3 | 80 | 1.229 | **483** | ≥ 450 ✔ |

- El detector ve el **96,8 %** de los datos personales insertados (1.762 de 1.821). Los que se le escapan son sobre todo oficios («la única veterinaria de…»), que no busca.
- El 13 % de los candidatos cae en el texto fijo de las plantillas: «Dña», «Magistrada», «Juzgado». Son falsos positivos muy parecidos a los del CENDOJ.

## Qué se aprendió

1. **Los textos sintéticos se delatan por detalles.** La primera versión generaba «Dña. Tomás» y «D. Lucía», porque los nombres se elegían sin tener en cuenta el género. Un modelo puede aprender que «si el tratamiento no concuerda con el nombre, es sintético», y la sonda de dominio lo detectaría. Se separaron los nombres por género y las plantillas ajustan el hueco al tratamiento.
2. **Qué es una «familia» decide qué mide el test.** Si cada familia fuera un tipo de dato (una de DNI, otra de teléfonos…), el test tendría tipos de dato que el modelo nunca vio y el criterio C2 fallaría por diseño. Con familias = tipos de documento, el test mide algo razonable: si el modelo generaliza a estructuras de documento nuevas.
3. **Las listas «disjuntas» no lo eran.** «Zamora» y «Toledo» eran a la vez apellido y municipio, y «Castaño», apellido y vía. Un test automático lo detectó antes de generar nada.
4. **El texto fijo de una plantilla no contiene datos personales por construcción.** No hace falta excluir los candidatos que caen ahí: son `NO` con certeza, y son justo los falsos positivos más útiles para entrenar. Esto cambia lo que decía el protocolo (desviación D4).
5. **Proporción de positivos:** ~40 % en el sintético frente al 15–20 % del CENDOJ. Es una diferencia de dominio que el modelo podría aprovechar como atajo. La sonda y el análisis por fuente lo vigilarán.

## Desviaciones del protocolo

| # | Sección | Cambio | Motivo | Efecto esperado |
|---|---|---|---|---|
| D4 | §3.1 | Los candidatos que no se solapan con ningún hueco se etiquetan `NO` en lugar de excluirse | El texto fijo de las plantillas no contiene datos personales, así que la etiqueta es cierta por construcción | Más negativos realistas (13 % de los candidatos); sin efecto sobre los positivos |

## Siguiente paso

Mientras se espera al CENDOJ: el código de los **Pasos 5–7** (sonda, baselines, entrenamiento y métricas C1–C3), probado **solo con la partición de entrenamiento**, para no mirar nunca calibración ni test antes de tiempo.

## Horas

2,5 h.

## Enlaces

- Issue: [#4](https://github.com/noelserdna/pii-judge-es-poc/issues/4) (sigue abierto hasta que lleguen las sentencias del CENDOJ)
