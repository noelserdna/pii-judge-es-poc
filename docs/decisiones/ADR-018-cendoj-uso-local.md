# ADR-018 · Las sentencias del CENDOJ se preparan y anotan en local ya; solo su publicación espera respuesta

**Estado:** aceptada · **Modifica:** [ADR-013](ADR-013-autorizacion-cendoj.md) · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: separar el uso local de la publicación.

## Contexto
El [ADR-013](ADR-013-autorizacion-cendoj.md) bloqueaba todo el Paso 3a hasta que el CENDOJ contestara, con el 24-11 como fecha límite. Al preparar la consulta se encontró que el **artículo 4.1 del Reglamento 3/2010** exime de licencia la reutilización por personas físicas para investigación científica sin finalidad comercial, que es el caso de este proyecto. Lo que puede requerir confirmación es la **publicación** de un conjunto derivado (manifiesto con identificadores y anotaciones por posiciones), no la consulta y el análisis en local.

Mientras tanto, el resto de piezas ya está listo: detector, corpus sintético, anotador, evaluación y Colab probado. La anotación humana del CENDOJ es ahora el único camino crítico.

## Decisión
- Se **descargan ya** unas 24 sentencias nuevas (≈ 6 por jurisdicción, 2024–2025, varios órganos), una a una y con pausas, **solo para uso local**.
- Se ejecutan el detector y el muestreo y se preparan los ficheros para el anotador, de modo que la anotación pueda empezar en cuanto haya tiempo.
- **No se publica** nada derivado de esas sentencias (manifiesto, offsets ni cifras por documento) hasta que conteste el CENDOJ o llegue el 24-11. Lo único que se publica son cifras agregadas, como en el chequeo.
- Si el CENDOJ dijera que hace falta autorización y no la concediera, las anotaciones quedarían en local, sin publicar, y se aplicaría la contingencia del protocolo (§3.4).

## Alternativas descartadas
- **Esperar al 24-11 sin hacer nada con el CENDOJ.** Retrasa el camino crítico dos semanas por una cuestión que afecta a la publicación, no al análisis.
- **Publicarlo todo ya amparándose en el art. 4.1.** Se envió una consulta y lo coherente es esperar la respuesta antes de publicar.

## Consecuencias
- Las 10 sentencias del chequeo siguen fuera de calibración y test (protocolo §3.2).
- El panel indica que las cifras del CENDOJ por documento son provisionales y locales.
