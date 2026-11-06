# ADR-007 · Apache-2.0 para código, CC BY 4.0 para documentación y datos

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí.

## Contexto
El repositorio mezcla código, documentación, datos sintéticos y anotaciones. Cada tipo de material tiene licencias habituales distintas.

## Decisión
- **Código** (`src/`, `tests/`, `tools/`, `notebooks/`): **Apache-2.0**. Incluye cláusula de patentes explícita y es aceptada en entornos empresariales y públicos.
- **Documentación, bitácora, guía didáctica, datos sintéticos y anotaciones por offsets**: **CC BY 4.0**.
- **Pesos de modelos**: no se publican (ADR-008).
- **Textos del CENDOJ**: no forman parte del repositorio; pertenecen a su titular.
- Se comprueba la licencia de las listas de nombres, municipios y calles que se usen para generar sintéticos y se anota en `data/synth/FUENTES.md`.

## Alternativas descartadas
- **MIT.** Aceptable, pero sin cláusula de patentes.
- **GPL.** Complicaría cualquier reutilización posterior.
- **CC0 para datos.** Se prefiere CC BY para que la autoría se mantenga visible.

## Consecuencias
Ficheros `LICENSE` (Apache-2.0), `LICENSE-docs` (CC BY 4.0) y sección «Licencias» en el README. `CITATION.cff` fija la forma de citar.
