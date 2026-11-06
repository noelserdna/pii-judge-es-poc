# ADR-009 · Cierre: firma, fechado externo (DOI) y archivado del repositorio

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí.

## Contexto
Para que un trabajo «cerrado y fechado» lo sea de verdad, las fechas tienen que ser verificables por un tercero y el cierre tiene que ser visible. Las fechas de git las pone el reloj del autor; las de una Release de GitHub y las de un depósito en Zenodo las pone el servidor.

## Decisión
- Todos los commits y tags van **firmados con SSH**; GitHub los muestra como «Verified».
- Cuatro tags firmados marcan los hitos: `preregistro` (protocolo cerrado, antes de experimentar), `guia-v1` (guía de anotación cerrada, antes de anotar), `anotacion-congelada` (etiquetas cerradas, antes de entrenar; su SHA-256 se publica en la bitácora) y `poc-v1` (informe final).
- `preregistro` y `poc-v1` tienen además una **Release** con el documento adjunto y un **DOI de Zenodo**.
- Tras `poc-v1`, el repositorio se **archiva** (solo lectura). El README indica fechas de inicio y cierre.

## Alternativas descartadas
- **Solo tags.** La fecha de un tag es editable por el autor.
- **Sellado criptográfico (OpenTimestamps).** Técnicamente más fuerte, pero menos legible para quien no es técnico; queda como opcional.

## Consecuencias
Hace falta vincular la cuenta de GitHub con Zenodo antes de la primera Release. Cualquier cambio tras `poc-v1` exigiría des-archivar, lo que quedaría registrado.
