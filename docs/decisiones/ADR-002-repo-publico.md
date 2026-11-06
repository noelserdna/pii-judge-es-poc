# ADR-002 · Repositorio público: lo publicado es estado de la técnica

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí, como criterio general de publicación.

## Contexto
Un repositorio público fechado es la forma más barata y verificable de demostrar que un trabajo existió, cuándo empezó y cuándo terminó. Pero publicar también significa divulgar: en Europa la novedad patentable es absoluta y cualquier divulgación previa la destruye.

## Decisión
El repositorio es **público** desde el primer commit. Todo lo que contiene es **técnica conocida** (clasificador de texto con marcadores de entidad, umbral fijado en calibración, baselines estándar) aplicada a un problema concreto. No se publica ninguna idea que pudiera ser objeto de protección; esas ideas, si existen, no forman parte de esta prueba de concepto.

## Alternativas descartadas
- **Repositorio privado.** Pierde el valor probatorio de la fecha pública y de la bitácora abierta, y GitHub Pages en privado exige cuenta de pago.
- **Público pero sin bitácora en tiempo real.** La bitácora con fallos y sorpresas es justo lo que da credibilidad al resultado final.

## Consecuencias
- Hay que estar dispuesto a que un resultado negativo sea público antes que cualquier informe.
- El README, los ADR y la bitácora se redactan sabiendo que cualquiera los lee.
- Al cerrar, el repositorio se archiva (ADR-009).
