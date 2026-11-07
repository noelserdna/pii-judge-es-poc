# ADR-005 · Entrenamiento en Google Colab; plan B en GPU local

**Estado:** sustituida por [ADR-014](ADR-014-computo-local.md) · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí, como criterio: datos públicos pueden salir a un tercero; datos no públicos, nunca.

## Contexto
El equipo local tiene una GTX 1060 de 3 GB. Basta para afinar DistilBETO con lotes pequeños, pero no para el modelo de referencia (roberta-base-bne, 125M) sin trucos. Google Colab ofrece una T4 (16 GB) gratis o casi.

## Decisión
Entrenar en **Colab**. Los únicos datos que se suben son los sintéticos y los contextos de sentencias públicas ya disociadas por el CENDOJ. **Se declara explícitamente** que eso implica enviar datos a un proveedor externo: es aceptable porque son públicos y disociados, y **no sería aceptable** con ningún documento no público.

Plan B si Colab falla: GTX 1060 con fp16, batch 8, acumulación de gradiente 4, max_len 192; el modelo de referencia se omite o se entrena con gradient checkpointing, y se documenta.

## Alternativas descartadas
- **Solo GPU local.** El modelo de referencia no cabe cómodamente y la varianza entre semillas exige varias corridas.
- **GPU alquilada.** Innecesario: el entrenamiento total son menos de dos horas de T4.

## Consecuencias
- Se registra el coste de Colab Pro, si se usa, en `costes.csv`.
- Se guarda `pip freeze` y el modelo de GPU en `reports/entorno-colab.txt` para reproducibilidad.
