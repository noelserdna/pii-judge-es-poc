# ADR-014 · Entrenamiento en la GPU local como opción principal; Colab como respaldo

**Estado:** aceptada · **Sustituye a:** [ADR-005](ADR-005-computo.md) · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: la prueba de humo como paso previo a cualquier entrenamiento.

## Contexto
El [ADR-005](ADR-005-computo.md) eligió Google Colab porque se suponía que la GTX 1060 de 3 GB no daba para el plan. Antes de preparar ningún notebook se ha medido (`tools/gpu_humo.py`: frases inventadas, max_len 192, 20 pasos tras 3 de calentamiento):

| Modelo | Configuración | Ejemplos/s | Memoria GPU máxima |
|---|---|---|---|
| DistilBETO (67M) | batch 8, FP32 | 33 | 1,3 GB |
| DistilBETO | batch 32, FP16 | 40 | 2,1 GB |
| RoBERTalex (125M) | batch 8, FP32 | 16,5 | 2,4 GB |
| RoBERTalex | batch 32 | 4,5 | 4,1 GB (desborda a memoria compartida) |

Otras comprobaciones:

- PyTorch 2.14 con CUDA 12.6 **sí** incluye la arquitectura de esta GPU (Pascal, sm_61). Las versiones con CUDA ≥ 12.8 empiezan a retirarla, así que hay que fijar el índice `cu126`.
- **FP16 no acelera nada** en Pascal, que no tiene tensor cores. Se entrena en FP32, que además es más reproducible.
- Con ~5.000 ejemplos de entrenamiento y 3 épocas, una corrida de DistilBETO tarda unos 6 minutos y una de RoBERTalex unos 15. Las ~24 corridas del protocolo suman **unas 3 horas** de GPU local.

## Decisión
- **Se entrena en local** (GTX 1060, PyTorch `2.14.1+cu126`, FP32).
- DistilBETO usa **batch 32 directamente**, como fija el protocolo.
- RoBERTalex usa **batch 8 con acumulación de gradiente ×4** (batch efectivo 32), porque batch 32 no cabe.
- **Colab queda como respaldo** si la GPU local falla o el calendario lo exige.

## Alternativas descartadas
- **Colab como opción principal.** Sería 4–5 veces más rápido, pero obliga a subir a Google los contextos de las sentencias y a depender de la disponibilidad de una T4 gratuita. Tres horas en local son asumibles.
- **FP16 en local.** No aporta velocidad en esta GPU.

## Consecuencias
- Los contextos del CENDOJ **no salen del ordenador** en ningún momento del proyecto.
- El fichero de entorno pasa a ser `reports/entorno.txt` (versiones de torch y transformers, GPU, driver).
- La acumulación de gradiente en RoBERTalex se registra como **desviación menor** del protocolo. Solo afecta a un análisis exploratorio (§9) y es matemáticamente equivalente salvo por el *dropout*.
