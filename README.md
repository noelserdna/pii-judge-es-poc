# PII-Judge-ES · prueba de concepto

**Estado:** prueba de concepto exploratoria e independiente, iniciada el 6 de noviembre de 2026. Cierre previsto en diciembre de 2026; al cerrar, el repositorio se archiva y queda de solo lectura.
**Financiación:** fondos propios de Andres Leon. Sin ayuda pública ni solicitud asociada.
**Página del proyecto (bitácora, decisiones, guía didáctica):** https://noelserdna.github.io/pii-judge-es-poc/

## Qué se investiga

Las herramientas que ocultan datos personales en sentencias y documentos administrativos cometen dos errores: tapan de más (un número de expediente tomado por un DNI, una ciudad tomada por un apellido) y dejan pasar datos que identifican a alguien por el contexto. Lo primero obliga a revisar a mano; lo segundo es una filtración.

**PII-Judge-ES** es la idea de poner, *después* de los detectores existentes (expresiones regulares, reconocimiento de entidades), un **validador pequeño** que mire cada candidato en su contexto y diga si de verdad es un dato personal. No es un detector: solo juzga lo que los detectores le pasan.

Esta prueba de concepto responde a **una sola pregunta**, fijada por escrito antes de hacer ningún experimento (ver `docs/protocolo.md` y el tag `preregistro`):

> ¿Un encoder de ≤ 100 MB en INT8, ejecutado en CPU, elimina al menos el 25 % de los falsos positivos del detector manteniendo los falsos descartes por debajo del 1 %, y lo hace mejor que una regresión logística?

## Lo que esta prueba de concepto NO demuestra

- No generaliza a documentos sin disociar ni a tipos documentales distintos de las sentencias.
- No da ninguna garantía estadística de riesgo: un umbral fijado en calibración no es una garantía.
- No prueba robustez frente a detectores o jurisdicciones no vistos (solo se explora, sin veredicto).
- No valida la etiqueta con un anotador jurídico independiente.
- No certifica anonimización. Es una herramienta de apoyo; la decisión de publicar un documento es siempre humana.

## Datos

- **Sintéticos**: generados por plantillas con etiqueta conocida por construcción. Se publican íntegros (`data/synth/`).
- **Sentencias del CENDOJ**: públicas y ya disociadas por el propio CENDOJ. **No se redistribuyen.** Se publica un manifiesto con sus identificadores y el hash SHA-256 de cada texto, y las anotaciones como posiciones (offsets) sin texto, para que cualquiera pueda reconstruir el conjunto descargando las mismas resoluciones.
- No se usan documentos reales de personas identificables fuera de esas fuentes públicas.

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | Página pública: panel de progreso, protocolo preregistrado, guía de anotación, bitácora, decisiones (ADR), guía didáctica, informe final |
| `src/` | Detector, generación de datos, particiones, baselines, evaluación |
| `tests/` | Pruebas unitarias |
| `notebooks/` | Entrenamiento en Colab |
| `data/` | Datos publicables (sintéticos, manifiesto, anotaciones por offsets) |
| `reports/` | Métricas, predicciones, registro de experimentos |
| `horas.csv`, `costes.csv` | Registro de esfuerzo y coste |

## Reproducir

```bash
uv sync --group dev --group docs
uv run pytest
uv run --group docs mkdocs serve
```

## Licencias

- Código: [Apache-2.0](LICENSE).
- Documentación, bitácora, guía y datos sintéticos: [CC BY 4.0](LICENSE-docs).
- Las resoluciones del CENDOJ pertenecen a su titular y no forman parte de este repositorio.
- Los pesos de los modelos entrenados no se publican.

## Trabajos posteriores

Cualquier trabajo que se apoye en esta prueba de concepto se documentará en otro repositorio y la citará como antecedente (ver `CITATION.cff`).
