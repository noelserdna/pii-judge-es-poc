# Plan de la prueba de concepto

> Versión pública del plan de trabajo. Fue revisado por tres perspectivas independientes (ingeniería de ML, estrategia y documentación, y una revisión deliberadamente escéptica) y consolidado por una moderación que resolvió los desacuerdos uno a uno. Los cambios posteriores se registran como ADR y en la bitácora; este fichero se actualiza para reflejarlos.

## Contexto

PII-Judge-ES es un **validador neuronal pequeño** (no un detector): recibe candidatos a dato personal encontrados por regex/NER en documentos jurídicos españoles y decide, en contexto, si lo son. Objetivo: **quitar falsos positivos sin descartar datos personales reales**.

Esta prueba de concepto es un **trabajo exploratorio independiente, cerrado y fechado, con fondos propios**, de una sola persona. Busca la primera evidencia experimental y hacer visible el progreso. Datos: sintéticos + sentencias públicas del CENDOJ, sin datos reales propios. Entrenamiento en Google Colab (T4); plan B en una GTX 1060 local. Inferencia medida en CPU local (i7-7700HQ).

**Fuera de esta prueba:** multitarea, destilación, un LLM como juez, garantías formales de riesgo bajo cambio de distribución, cuasi-identificadores. Solo un umbral fijado en calibración.

## Pregunta y criterios preregistrados

> ¿Un encoder ≤ 100 MB INT8 (DistilBETO + marcadores de entidad con señal de mayúscula) elimina ≥ 25 % de los falsos positivos del detector frente a «aceptar todos», manteniendo los falsos descartes ≤ 1 %, y supera a una regresión logística reforzada?

**Conjuntos.** Cal = calibración agrupada (sintético cal ∪ CENDOJ cal). T = test agrupado (familias sintéticas no vistas ∪ documentos CENDOJ no vistos), diseñado para ≥ 500 positivos y ≥ 500 negativos. τ se fija en Cal como el umbral que deja FNR ≤ 1 % en Cal.

**Modelo evaluado.** Semilla mediana (en % FP eliminados en Cal) de 3 semillas de DistilBETO. Hiperparámetros fijos: 3 épocas, lr 3e-5, batch 32, max_len 192, warmup 10 %, weight decay 0,01, último epoch sin early stopping.

**Nivel 1 — criterios de éxito (pasa / no concluyente / no pasa), sobre T:**

| Criterio | Pasa | No concluyente | No pasa |
|---|---|---|---|
| C1 FP eliminados vs aceptar-todos a τ | cota inferior IC 95 % (bootstrap pareado por documento/familia, 2.000 réplicas) ≥ 25 % | punto ≥ 25 % y cota inferior < 25 % | punto < 25 % |
| C2 Falsos descartes a τ (T con ≥ 500 positivos) | FNR puntual ≤ 1 % **y** cota superior Clopper-Pearson 95 % ≤ 2,5 % | punto ≤ 1 % y CP > 2,5 % | punto > 1 % |
| C3 Supera a LR | Δ (modelo − LR) en % FP eliminados al mismo FNR objetivo ≥ 5 puntos **y** cota inferior IC 95 % pareado > 0 | Δ ≥ 5 y cota inferior ≤ 0 | Δ < 5 |

**Nivel 2 — CENDOJ descriptivo (sin veredicto):** FNR puntual + cota CP 95 %; % FP eliminados con IC; curva riesgo–cobertura (ε ∈ {1, 2, 5} %); desglosado por `rol`.

**Exploratorio (no preregistrado, sin umbral ni veredicto):** cortes sintético→CENDOJ, detector no visto (Presidio), jurisdicción cruzada; ablaciones solo-candidato, solo-contexto, sin señal de mayúscula, train sin CENDOJ; curva de aprendizaje 25/50/100 %; roberta-base-bne como techo; caída FP32→INT8.

**Lo que esta prueba NO demuestra:** generalización a documentos no disociados ni a otros tipos documentales; garantía estadística de riesgo; robustez a detectores o jurisdicciones no vistas (solo se explora); validez de la etiqueta sin anotador jurídico independiente.

## Qué hace falta

| Recurso | Detalle |
|---|---|
| Python | uv + Python 3.11 |
| Librerías | spaCy + `es_core_news_lg`, presidio-analyzer, scikit-learn, transformers, datasets, torch, optimum, onnxruntime, pandas, mkdocs-material, pytest |
| Cuentas | Google (Colab), Hugging Face, Zenodo |
| Modelos base | `dccuchile/distilbert-base-spanish-uncased` (principal); `PlanTL-GOB-ES/roberta-base-bne` (referencia cased) |
| Datos | 10–12 familias sintéticas (~3.000 candidatos; ≥ 450 positivos en familias de test); 20–25 sentencias CENDOJ estratificadas por jurisdicción → 1.500–2.000 candidatos anotados al 100 % |
| Personas | Una. Segundo anotador si hay perfil jurídico; si no, re-anotación propia a ciegas ≥ 7 días después del congelado |
| Tiempo | ~106 h (88 de experimento + 18 de guía didáctica); límite duro 16-12-2026 |

## Documentación del proceso

- **Repositorio público** con commits y tags firmados (SSH). Ver [ADR-002](docs/decisiones/ADR-002-repo-publico.md) y [ADR-008](docs/decisiones/ADR-008-que-se-publica.md) para qué se publica y qué no.
- **Flujo git:** issue por paso + milestone; commits directos a `main` con `#N`; PR solo en pasos con código (2, 5, 7); tags firmados `preregistro`, `guia-v1`, `anotacion-congelada`, `poc-v1`; Release + DOI en el primero y el último; archivado al cerrar.
- **Página** (MkDocs Material): panel de progreso, protocolo, guía de anotación, bitácora por sesión, ADR, guía didáctica, informe.
- **Registros:** `horas.csv`, `costes.csv`, `reports/experimentos.csv`.

## Guía didáctica

Un capítulo por paso en `docs/guia/`, escrito al cerrar cada paso, con tres hilos (crear un modelo · proteger datos · herramientas), plantilla fija (qué y por qué → conceptos con analogía → visual → código comentado → errores típicos → autoevaluación → para profundizar) y recursos visuales reproducibles (Mermaid, figuras por script en `tools/figuras/`, ejemplos sintéticos).

## Paso a paso (fechas orientativas)

La única regla de orden: **el preregistro (tag + DOI) se publica antes de entrenar nada.**

| # | Paso | Fechas | Horas | Hito |
|---|---|---|---|---|
| 0 | Proyecto, repo, chequeo de realidad sobre 10 sentencias, protocolo | 7–10 nov | 12 | `preregistro` |
| 1 | Guía de anotación v1 (regla contrafactual, roles, ambiguos) | 11–12 nov | 4 | `guia-v1` |
| 2 | Detector de alta sensibilidad (regex + spaCy) + Presidio para test · PR | 12–14 nov | 8 | |
| 3 | Datos: 20–25 sentencias CENDOJ, 10–12 familias sintéticas, candidatos, anotación al 100 % (parada dura a 20 h) | 15–24 nov | 33 | |
| 4 | Congelado de etiquetas y manifiesto de particiones | 25 nov | 3 | `anotacion-congelada` |
| 5 | Sonda sintético-vs-real, aceptar-todos, regresión logística reforzada · PR | 26 nov | 4 | |
| 6 | Entrenamiento en Colab: DistilBETO ×3 semillas, ablaciones, curva de aprendizaje, roberta-base-bne | 27–28 nov | 8 | |
| 7 | Evaluación: C1–C3, CENDOJ descriptivo, exploratorio, ONNX INT8, latencia; re-anotación a ciegas (κ) · PR | 29 nov – 1 dic | 10 | |
| 7b | (Opcional) tipo documental no visto con MEDDOCAN | 2 dic | 4 | |
| 8 | Informe, Release, DOI, archivado | 3–4 dic | 6 | `poc-v1` |
| — | Guía didáctica, un capítulo al cierre de cada paso | continuo | 18 | |

## Verificación

- `pytest` en CI: checksums DNI/NIE; spans de frases conocidas; fusión de solapamientos; coherencia de etiquetas sintéticas; particiones sin documentos/familias compartidas y gazetteers disjuntas; métricas sobre un fixture con resultados conocidos.
- Humo en CPU antes de Colab: detector → sintéticos → particiones → sonda → regresión logística → métricas.
- Notebook: misma semilla → mismas predicciones al reexportar en CPU; variabilidad entre semillas reportada.
- Informe: cada criterio con punto, intervalo y veredicto.
- Documentación: `mkdocs build --strict` sin errores; workflow en verde; tags firmados verificables; Releases con DOI.
- Antes de cada push: `git ls-files` sin nada de `data/cendoj/raw`, `data/cendoj/candidates` ni checkpoints.

## Riesgos conocidos

- Anotador = modelador: la re-anotación mide consistencia, no validez jurídica.
- Positivos del CENDOJ dominados por nombres en posiciones formularias.
- Circularidad plantillas = detector = autor: la sonda la diagnostica, no la elimina.
- Calendario de una sola persona: la anotación y la disponibilidad de GPU en Colab son los cuellos de botella.
