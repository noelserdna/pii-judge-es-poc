# ADR-006 · DistilBETO con señal de mayúscula como candidato; roberta-base-bne como referencia

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí: el esquema de marcadores y la señal de mayúscula.

## Contexto
El presupuesto del candidato es ≤ 100 MB en INT8 y latencia baja en CPU. Los encoders en español disponibles: DistilBETO (67M, **uncased**), BETO cased (110M), roberta-base-bne / RoBERTalex (125M, cased), multilingüe recortado (~65M tras recortar vocabulario). Un modelo *uncased* convierte todo a minúsculas y pierde la distinción «Cuenca» (ciudad o apellido) / «cuenca» (sustantivo), que es una de las señales principales de este problema.

## Decisión
- **Candidato principal:** `dccuchile/distilbert-base-spanish-uncased` (DistilBETO), con dos compensaciones: marcadores de entidad hechos con **tokens que ya existen** en el vocabulario (no tokens nuevos con embeddings aleatorios) y un **token de señal de mayúscula** (inicial / todo mayúsculas / minúscula) delante del span. Los criterios preregistrados se evalúan sobre este modelo.
- **Referencia de techo:** `PlanTL-GOB-ES/roberta-base-bne` (cased, 125M, fuera del presupuesto de tamaño) con los mismos hiperparámetros, para medir «cuánto cuesta ser pequeño». Resultado exploratorio.
- **Ablación:** DistilBETO sin la señal de mayúscula, para saber si la señal importa.

## Alternativas descartadas
- **Solo DistilBETO sin compensar.** Si pierde contra la regresión logística (que sí ve mayúsculas) no sabríamos si es por tamaño o por casing.
- **BETO cased como tercer modelo.** La ablación con/sin señal responde a la pregunta de la mayúscula sin otro modelo.
- **Modelo multilingüe con vocabulario recortado.** Medio día de trabajo que no cambia la pregunta; queda para después.

## Consecuencias
- Hiperparámetros fijos en el protocolo (sin búsqueda): 3 épocas, lr 3e-5, batch 32, max_len 192, warmup 10 %, weight decay 0,01, último epoch.
- 3 semillas por configuración; se reporta la mediana y la dispersión.
