# ADR-008 · Qué se publica y qué no

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí, como lista de control.

## Contexto
La reproducibilidad pide publicar lo máximo; la protección de datos y el respeto a las fuentes piden publicar lo mínimo. Hay que fijar la frontera.

## Decisión
**Se publica:**

- Generador y corpus sintético completos (`data/synth/`).
- `data/cendoj/manifiesto-cendoj.csv`: identificador de cada resolución (ROJ/ECLI), URL del buscador, SHA-256 del texto extraído, jurisdicción y partición asignada.
- Anotaciones del CENDOJ **como offsets sin texto**: `doc_id, start, end, label, rol, ambiguo`.
- Predicciones por candidato (identificador y probabilidad, por modelo y semilla), `reports/metrics.json`, `reports/experimentos.csv`, `reports/entorno-colab.txt`.
- `horas.csv` y `costes.csv`.

**No se publica:**

- Textos de las resoluciones ni los contextos de ±200 caracteres de sus candidatos (`data/cendoj/raw/`, `data/cendoj/candidates/`).
- Pesos de modelos (checkpoints, ONNX).
- Ningún documento ajeno a la prueba de concepto.

## Alternativas descartadas
- **Publicar los contextos del CENDOJ** «porque ya son públicos». Redistribuir fragmentos de resoluciones no es lo mismo que enlazarlas; los offsets más el hash permiten reconstruirlos a quien descargue las mismas resoluciones.
- **Publicar los pesos.** Un modelo puede memorizar fragmentos de su entrenamiento y no hay tiempo para pruebas de extracción.

## Consecuencias
`.gitignore` refleja la lista. Antes de cada push se comprueba que `git ls-files` no contenga nada de las rutas excluidas.
