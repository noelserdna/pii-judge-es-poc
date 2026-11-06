# ADR-011 · Documentación mínima con trazabilidad: MkDocs, bitácora por sesión, flujo git

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí.

## Contexto
Una persona sola. La documentación tiene que dejar constancia verificable de qué se hizo, qué se decidió y qué se aprendió, y servir de guía didáctica, sin consumir el tiempo que necesitan los datos y los experimentos.

## Decisión
- **Página** con **MkDocs Material** (mismo stack Python, tema claro/oscuro, móvil, búsqueda, diagramas Mermaid). Cero HTML escrito a mano. Publicada por GitHub Actions en cada push a `main`.
- **Bitácora por sesión** (`docs/blog/posts/AAAA-MM-DD.md`) con plantilla fija: qué se hizo, decisiones, qué se aprendió (fallos y sorpresas), cifras, **desviaciones del protocolo**, siguiente paso, horas, enlaces. Entrada de cierre al terminar cada paso.
- **ADR** cortos, escritos una vez; cambios → ADR nuevo.
- **Guía didáctica** (`docs/guia/`): un capítulo por paso, escrito al cerrar el paso, con plantilla fija y recursos visuales reproducibles (Mermaid, figuras por script, ejemplos sintéticos).
- **Flujo git:** un issue por paso con milestone; commits directos a `main` con `#N`; PR solo en pasos con código (gate de tests); cuatro tags firmados. `main` sin protección.
- **Registros:** `horas.csv`, `costes.csv`, `reports/experimentos.csv` desde el día 1.
- Tope: ≤ 15 h de bitácora, ADR y página en toda la prueba; la guía didáctica (~18 h) va aparte.

## Alternativas descartadas
- **Generador de sitio propio en Python.** Horas de HTML/CSS que no producen evidencia.
- **Jekyll (tema por defecto de GitHub Pages).** Exige Ruby para probar en local y no da blog ni Mermaid sin plugins.
- **Issue + rama + PR por cada paso.** Un PR que una sola persona se aprueba no revisa nada; para documentación es fricción pura.

## Consecuencias
Panel de indicadores en `docs/index.md`, mantenido a mano en cada sesión. La guía se escribe después de cada paso, nunca antes.
