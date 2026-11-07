---
date: 2026-11-07
categories:
  - Paso 3
  - Paso 5
  - Paso 6
  - Paso 7
---

# Todo listo salvo lo que solo puede hacer una persona: anotar

Mientras se espera la respuesta del CENDOJ, se ha preparado todo lo demás. Al terminar el día solo queda un trabajo en el camino crítico: **anotar a mano 1.642 candidatos de 24 sentencias**. Detrás de esa anotación, todo está automatizado y probado.

<!-- more -->

## Qué se hizo

- **[ADR-018](../../decisiones/ADR-018-cendoj-uso-local.md):** las sentencias se descargan y se preparan **en local** ya, amparándose en el art. 4.1 del Reglamento 3/2010. Solo la **publicación** del manifiesto y de las anotaciones espera la respuesta del CENDOJ.
- **24 sentencias nuevas** de 2024: 6 por jurisdicción, mitad de Audiencias Provinciales o TSJ y mitad del Tribunal Supremo, de 11 provincias distintas. Se evitaron a propósito las causas por delitos sexuales y las sentencias centradas en la salud, para tratar el mínimo de datos especialmente protegidos.
- **Pipeline del CENDOJ** (`src/data/cendoj.py`):
    - extracción de texto y SHA-256;
    - particiones por documento **antes de anotar**: 10 de entrenamiento, 4 de calibración y 10 de test;
    - detector y muestreo de hasta 70 grupos por sentencia;
    - Presidio en las sentencias de test, como detector no visto;
    - fichero para el anotador y reconstrucción de instancias, con propagación de etiquetas en entrenamiento.
- **Código de los Pasos 5–7** ([PR #12](https://github.com/noelserdna/pii-judge-es-poc/pull/12)): regresión logística reforzada, afinado con todas las variantes del protocolo, métricas C1–C3 con bootstrap por documento y el evaluador completo.
- **Orquestador de Colab** (`tools/colab_entrenar.py`): crea la sesión con T4, sube las instancias, lanza las 24 corridas, descarga las predicciones, guarda las versiones del entorno y **siempre** libera la sesión.

## Cifras

| | |
|---|---|
| Candidatos del detector en las 24 sentencias | 3.877 |
| Instancias que hay que anotar | **1.642** (entrenamiento 674 · calibración 273 · test 662 · Presidio 33) |
| Tiempo estimado de anotación (a 4,6–8 s cada una) | 2–3,5 h |
| Prueba de humo del orquestador en Colab (T4) | 41 s por corrida corta; sesión creada y liberada sin intervención |
| Unidades de Colab consumidas hasta hoy | 0,03 de 160 |
| Tests | 32 en verde |

## Qué se aprendió

1. **El código de evaluación se puede probar sin mirar el test.** Se partió la partición de entrenamiento en un «calibración» y un «test» falsos y se ejecutó la cadena completa: entrenar, fijar el umbral, bootstrap y veredictos. Así se depuró el código sin que ninguna decisión pudiera verse influida por los resultados reales.
2. **La regresión logística acierta casi todo cuando calibración y test comparten plantillas con el entrenamiento.** En la prueba de humo, con calibración y test sacados de las mismas familias sintéticas que el entrenamiento, la regresión logística apenas se equivocó. No es un resultado: es la confirmación de que hay que evaluar con **familias no vistas**, como hace el protocolo. Si no, un modelo que memoriza plantillas parece perfecto.
3. **El marcador `«»` no existe en el vocabulario de DistilBETO** (se convierte en `[UNK]`), así que se usan corchetes `[ ]`, que existen en los dos modelos. Es un detalle que, sin comprobarlo, habría dejado al modelo sin saber dónde empieza el candidato.
4. **Las sugerencias de la IA se descartan para la anotación principal** ([ADR-015](../../decisiones/ADR-015-anotacion-ciega.md)). Generar 1.642 a mano no es viable, y generarlas con un modelo del propio proyecto metería su sesgo en las etiquetas.

## Desviaciones del protocolo

Ninguna nueva.

## Siguiente paso

**Anotar** las 1.642 instancias con el anotador en modo ciego. Después: congelado de etiquetas (`anotacion-congelada`), entrenamiento en Colab, evaluación e informe.

## Horas

4 h.

## Enlaces

- Issues: [#4](https://github.com/noelserdna/pii-judge-es-poc/issues/4) · [#6](https://github.com/noelserdna/pii-judge-es-poc/issues/6) · [#7](https://github.com/noelserdna/pii-judge-es-poc/issues/7) · [#8](https://github.com/noelserdna/pii-judge-es-poc/issues/8)
