# ADR-010 · Cómo se etiqueta un texto ya disociado

**Estado:** propuesta (se confirma tras el chequeo de realidad sobre 10 sentencias) · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí: la regla contrafactual y los roles.

## Contexto
El CENDOJ no borra los datos personales: **sustituye** los nombres de las partes por otros nombres (p. ej. «D. Eutimio», «Dña. Candelaria») y los identificadores por marcadores («NUM000», «DIRECCION000», «CALLE000»). Los nombres de magistrados, letrados, procuradores y letrados de la Administración de Justicia suelen conservarse. Si la pregunta de anotación fuera literalmente «¿es un dato personal de una persona identificable?», «D. Eutimio» sería **no** (es ficticio) y el modelo aprendería que los nombres de las partes no son datos personales: lo contrario de lo que debe aprender.

## Decisión
- **Regla contrafactual:** la pregunta es «si este documento **no** estuviera disociado, ¿este span identificaría a una persona física?».
- **Pseudónimos de partes** (nombres que el CENDOJ ha puesto en lugar de los reales) → **SÍ**, con `rol = parte`.
- **Marcadores** (NUM000, DIRECCION000, CALLE000, etc.) → se **excluyen** del conjunto de candidatos (`EXCLUIDO_PLACEHOLDER`) y se cuentan. Son un atajo trivial.
- **Magistrados, letrados, procuradores, LAJ, peritos** → **SÍ**, con `rol ∈ {judicial, profesional}`. Son personas físicas identificadas aunque en la práctica no se redacten; el campo `rol` permite separar ese estrato al evaluar.
- **Ambiguo** solo si el contexto de ±200 caracteres no permite decidir. Se excluye de entrenamiento, calibración y test, y se reporta el porcentaje. Objetivo < 5 %; más del 10 % es una desviación que se documenta.

## Alternativas descartadas
- **Pregunta literal del art. 4.1 RGPD.** Por el efecto perverso descrito.
- **Etiquetar a los profesionales como NO** «porque no se redactan». Mezcla «es dato personal» con «debe redactarse», que son preguntas distintas. La segunda es de política, no del modelo.

## Consecuencias
- Los positivos del CENDOJ estarán dominados por nombres en posiciones formularias («Magistrado D. …»). La evaluación se desglosa por `rol` para ver si el modelo aprende solo eso.
- Las categorías IDENTIFICADOR y DIRECCIÓN no tendrán positivos reales en CENDOJ (son marcadores); solo se miden en sintético. Se declara en «Lo que esta PoC NO demuestra».
