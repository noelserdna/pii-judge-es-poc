# Registro de decisiones (ADR)

Cada decisión relevante se registra una vez, con su contexto, las alternativas descartadas y sus consecuencias. Si una decisión cambia, no se edita: se escribe un ADR nuevo que la sustituye y el antiguo pasa a estado «sustituida».

| Nº | Decisión | Estado | Fecha |
|---|---|---|---|
| [001](ADR-001-poc-independiente.md) | Prueba de concepto exploratoria, independiente y con fondos propios | aceptada | 2026-11-06 |
| [002](ADR-002-repo-publico.md) | Repositorio público: lo publicado es estado de la técnica | aceptada | 2026-11-06 |
| [003](ADR-003-datos.md) | Datos sintéticos + sentencias públicas del CENDOJ; sin datos reales propios | aceptada | 2026-11-06 |
| [004](ADR-004-detector.md) | Detector propio para entrenar y evaluar; Presidio solo en test como detector no visto | aceptada | 2026-11-06 |
| [005](ADR-005-computo.md) | Entrenamiento en Google Colab; plan B en GPU local | sustituida por 014 | 2026-11-06 |
| [006](ADR-006-modelo.md) | DistilBETO con señal de mayúscula como candidato; roberta-base-bne como referencia | aceptada | 2026-11-06 |
| [007](ADR-007-licencias.md) | Apache-2.0 para código, CC BY 4.0 para documentación y datos | aceptada | 2026-11-06 |
| [008](ADR-008-que-se-publica.md) | Qué se publica y qué no | aceptada | 2026-11-06 |
| [009](ADR-009-cierre.md) | Cierre: firma, fechado externo (DOI) y archivado del repositorio | aceptada | 2026-11-06 |
| [010](ADR-010-etiqueta-cendoj.md) | Cómo se etiqueta un texto ya disociado | aceptada | 2026-11-07 |
| [011](ADR-011-documentacion.md) | Documentación mínima con trazabilidad: MkDocs, bitácora por sesión, flujo git | aceptada | 2026-11-06 |
| [012](ADR-012-unidad-de-anotacion.md) | Unidad de anotación: una mención por grupo y muestreo por documento | aceptada | 2026-11-07 |
| [013](ADR-013-autorizacion-cendoj.md) | El uso del CENDOJ más allá del chequeo queda condicionado a su autorización | aceptada | 2026-11-07 |
| [014](ADR-014-computo-local.md) | Entrenamiento en la GPU local como opción principal; Colab como respaldo | sustituida por 016 | 2026-11-07 |
| [015](ADR-015-anotacion-ciega.md) | Toda la anotación se hace en modo ciego | aceptada | 2026-11-07 |
| [016](ADR-016-colab.md) | Corridas de entrenamiento en Colab; GPU local para desarrollo y respaldo | aceptada | 2026-11-07 |
| [017](ADR-017-sinteticos.md) | Diseño del corpus sintético: familias = tipos de documento | aceptada | 2026-11-07 |
| [018](ADR-018-cendoj-uso-local.md) | Las sentencias del CENDOJ se preparan y anotan en local; solo su publicación espera respuesta | aceptada | 2026-11-07 |
