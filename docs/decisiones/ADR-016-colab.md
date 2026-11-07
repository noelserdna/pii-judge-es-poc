# ADR-016 · Las corridas de entrenamiento se hacen en Google Colab; la GPU local, para desarrollo y respaldo

**Estado:** aceptada · **Sustituye a:** [ADR-014](ADR-014-computo-local.md) · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: el criterio de qué datos pueden salir a un tercero.

## Contexto
El [ADR-014](ADR-014-computo-local.md) eligió la GPU local porque todo el entrenamiento cabía en unas 3 h. Después se estimó el coste en Colab: una T4 consume del orden de 2 unidades de computación por hora y es 4–5 veces más rápida que la GTX 1060, así que todas las corridas costarían **unas 2–5 unidades**. El autor dispone de **160 unidades** en su cuenta. No hay coste nuevo y se gana tiempo de calendario: unas 3 h de GPU local frente a menos de 1 h en Colab.

## Decisión
- Las **corridas del protocolo** (DistilBETO ×3 semillas, ablaciones, curva de aprendizaje y RoBERTalex) se hacen en **Colab**, con la GPU que haya disponible (T4 o superior).
- La **GPU local** se usa para la prueba de humo, el desarrollo del código de entrenamiento con datos de entrenamiento y como **respaldo** si Colab falla.
- Datos que se suben a Colab, y solo durante la sesión: sintéticos y **contextos de sentencias públicas ya disociadas por el CENDOJ**. Es el mismo criterio del [ADR-005](ADR-005-computo.md): aceptable porque son públicos y disociados; **no lo sería** con ningún documento no público.
- Se usan las mismas versiones de torch y transformers que en local, se guarda `pip freeze` y el modelo de GPU en `reports/entorno-colab.txt`, y se anotan las unidades consumidas en `costes.csv` (0 €, porque son unidades ya disponibles).

## Alternativas descartadas
- **Solo en local** ([ADR-014](ADR-014-computo-local.md)). Viable, pero más lento, y las unidades de Colab ya están pagadas.

## Consecuencias
- Las desviaciones D2 (acumulación de gradiente en RoBERTalex) y D3 (nombre del fichero de entorno) de la [bitácora del 7-11](../blog/posts/2026-11-07-prueba-guia-y-gpu.md) **dejan de aplicarse**: en una T4 RoBERTalex cabe con batch 32 y el fichero vuelve a llamarse `reports/entorno-colab.txt`, como dice el protocolo.
- El notebook tiene que ser reproducible desde un clon limpio del repositorio, con los datos subidos a Drive.
