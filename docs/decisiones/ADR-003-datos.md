# ADR-003 · Datos sintéticos + sentencias públicas del CENDOJ; sin datos reales propios

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Parcialmente: los sintéticos sí; el uso del CENDOJ para otros fines exige revisar su licencia.

## Contexto
El validador necesita candidatos con su contexto y una etiqueta fiable. Las opciones eran: documentos reales propios (con riesgo legal y necesidad de evaluación de impacto), sentencias públicas del CENDOJ (ya disociadas por el propio órgano) y datos sintéticos generados por plantillas.

## Decisión
- **Sintéticos** por plantillas con pares contrastivos (la misma palabra en un contexto donde es dato personal y en otro donde no lo es). Etiqueta conocida por construcción. Son los únicos datos que se publican íntegros.
- **Sentencias del CENDOJ**, descargadas a mano del buscador público, para medir sobre texto real. Están disociadas: las partes aparecen con pseudónimos y los identificadores con marcadores (NUM000, DIRECCION000). Se usan en local y **no se redistribuyen**: se publica un manifiesto (identificador, hash SHA-256) y las anotaciones como posiciones sin texto.
- **Ningún documento real propio** ni de terceros identificables.

## Alternativas descartadas
- **Documentos reales de despachos o administraciones.** Exige base jurídica, contrato y evaluación de impacto; desproporcionado para una prueba de concepto.
- **Boletines oficiales (edictos con nombres y DNI parciales).** Son datos personales reales de personas identificables aunque sean públicos; viola «sin datos reales propios».
- **Corpus anotados de terceros (MEDDOCAN, MAPA).** No se descartan del todo: MEDDOCAN (clínico, CC BY 4.0) queda como anexo exploratorio opcional si sobra tiempo. MAPA se descarta por licencia no verificable a tiempo.

## Consecuencias
- Los positivos reales del CENDOJ serán escasos y de un tipo concreto (pseudónimos de partes, nombres de profesionales). La mayoría de positivos del test vendrán de los sintéticos. El protocolo lo tiene en cuenta (ADR-010 y `docs/protocolo.md`).
- Hay que revisar el aviso legal del CENDOJ antes de descargar y documentar la revisión en la bitácora.
