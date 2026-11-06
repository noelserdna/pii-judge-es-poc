# Protocolo preregistrado

!!! danger "BORRADOR v0 · pendiente de revisión"
    Este documento **todavía no está cerrado**. Se cerrará con el tag firmado `preregistro`, una Release y un DOI de Zenodo. Desde ese momento, cualquier cambio se registrará como **desviación** en la bitácora, con fecha y motivo.

**Versión:** 0 (borrador) · **Autor:** Andres Leon · **Fecha:** 7-11-2026

## 1. Pregunta

> ¿Un encoder de ≤ 100 MB en INT8 (DistilBETO + marcadores de entidad con señal de mayúscula) elimina **≥ 25 %** de los falsos positivos del detector frente a «aceptar todos», mantiene los **falsos descartes ≤ 1 %** y **supera a una regresión logística** reforzada?

## 2. Definiciones

| Término | Definición operativa |
|---|---|
| **Candidato** | Un span de texto que el detector marca como posible dato personal, con su posición en el documento. |
| **Grupo** | Conjunto de candidatos de un mismo documento con la misma forma normalizada (minúsculas, sin tratamientos como «Sr.» o «Dña.», sin puntuación en los extremos) y la misma etiqueta del detector ([ADR-012](decisiones/ADR-012-unidad-de-anotacion.md)). |
| **Instancia** | Una mención de un grupo elegida al azar con semilla fija, con ±200 caracteres de contexto. Es la unidad de anotación y de evaluación. |
| **Positivo** | Instancia etiquetada SÍ según la [guía de anotación](guia-anotacion.md): con la regla contrafactual, identificaría a una persona física. |
| **Puntuación** | Probabilidad de «positivo» que asigna un modelo a una instancia. |
| **τ (umbral)** | Valor que separa las decisiones: puntuación ≥ τ → se trata como dato personal; puntuación < τ → se **descarta** (se conserva el texto). |
| **Falso descarte (FN)** | Positivo con puntuación < τ. **FNR** = FN / positivos. |
| **Falso positivo eliminado** | Negativo con puntuación < τ. **% FP eliminados** = negativos descartados / negativos = tasa de verdaderos negativos (TNR). «Aceptar todos» tiene 0 % de FP eliminados y 0 % de FNR. |

## 3. Datos

### 3.1 Sintéticos

- **10–12 familias de plantillas** con pares contrastivos: la misma superficie en un contexto donde es dato personal y en otro donde no. Se generan con `src/data/synth.py` y semilla fija.
- **Partición por familia:** entrenamiento (≥ 6 familias), calibración (2), test (3). Un par contrastivo nunca se separa.
- **Gazetteers disjuntas por partición:** ningún nombre, apellido, municipio ni calle aparece en dos particiones.
- **Mínimos garantizados por el generador:** ≥ 300 positivos en calibración y ≥ 450 en test.
- Cada texto generado es un **documento sintético**, y el bootstrap (§6) lo trata como unidad.
- La etiqueta se conoce por construcción. Los candidatos del detector que no coinciden con un slot ni con un span fijo etiquetado se excluyen y se cuentan (< 5 %).

### 3.2 CENDOJ (condicionado a la autorización, [ADR-013](decisiones/ADR-013-autorizacion-cendoj.md))

- **~25 sentencias** en español de 2024–2025, ≈ 6 por jurisdicción (civil, penal, social, contencioso), de varios órganos.
- Las **10 sentencias del chequeo de realidad quedan fuera** de calibración y test, porque ya se han leído.
- **Partición por documento 40 / 20 / 40** (train / cal / test), estratificada por jurisdicción y asignada **antes de anotar**, con semilla fija (`src/data/split.py`).
- **Muestreo:** de cada sentencia, hasta **70 grupos** al azar, estratificados por etiqueta del detector, y una instancia por grupo. Se excluyen los grupos cuyo span es un marcador de disociación (`NUM000`, `DIRECCION000`…) y se cuentan.
- En train, la etiqueta se propaga a las demás menciones del grupo. En cal y test no hay propagación.

### 3.3 Conjuntos de evaluación

- **Cal** = sintético cal ∪ CENDOJ cal.
- **T** = sintético test ∪ CENDOJ test. Objetivo: ≥ 500 positivos y ≥ 500 negativos.

### 3.4 Contingencia preregistrada

Si el **24-11-2026** no se ha obtenido la autorización de reutilización del CENDOJ:

- Cal y T son **solo sintéticos**, con los mismos mínimos.
- El Nivel 2 (§8) **no se realiza**.
- El informe lo declara en primera página como limitación principal.

Aplicar esta contingencia **no** cuenta como desviación, porque queda fijada aquí.

## 4. Anotación

- Se sigue la [guía de anotación](guia-anotacion.md) v1, que se cierra con el tag `guia-v1` **antes** de anotar.
- **Etiquetas:** `SI`, `NO`, `AMBIGUO`, `EXCLUIDO_PLACEHOLDER`, con categoría y `rol`.
- **La etiqueta del detector no se muestra** al anotador. El orden de las instancias es aleatorio.
- Las instancias `AMBIGUO` se excluyen de train, cal y test. Se reporta su porcentaje: se espera menos del 5 %, y más del 10 % se trata como desviación.
- **Congelado:** el tag `anotacion-congelada` se firma antes de entrenar ningún modelo y el SHA-256 de los ficheros de anotación se publica en la bitácora.
- **Acuerdo:** se reanotan 100 instancias de T, elegidas al azar, al menos 7 días después del congelado y sin ver la etiqueta anterior (o las anota una segunda persona si la hay). Se reporta κ de Cohen con IC 95 %. Si κ < 0,6, el informe lo declara en primera página.

## 5. Modelos

| Modelo | Papel | Detalle |
|---|---|---|
| **Aceptar todos** | Referencia | Todas las instancias, puntuación 1. |
| **Regresión logística (LR)** | Baseline | Features: etiqueta del detector, validez del checksum, disparadores léxicos («D.», «Dña.», «calle», «expediente», «Juzgado»…), forma de mayúsculas, longitud, TF-IDF de n-gramas de caracteres 2–5 del span y bolsa de palabras de ±5 tokens de contexto. `C = 1.0`, `class_weight = balanced`, sin búsqueda de hiperparámetros. |
| **DistilBETO** (candidato) | Modelo evaluado | `dccuchile/distilbert-base-spanish-uncased`. Entrada: contexto con el span entre marcadores formados por tokens existentes del vocabulario, precedido de un token de mayúscula (`inicial` / `todo` / `minuscula`). 3 épocas, lr 3e-5, batch 32, max_len 192, warmup 10 %, weight decay 0,01, se usa el **último epoch** (sin early stopping ni selección). |

**Semillas:** 13, 42 y 2026. El **modelo evaluado** en C1–C3 es la semilla **mediana** por % FP eliminados en Cal. Las otras dos se reportan.

**Restricción de tamaño:** el modelo exportado a ONNX y cuantizado a INT8 (`quantize_dynamic`, `reduce_range=True`) debe ocupar ≤ 100 MB. Si no lo cumple, el resultado se reporta, pero C1–C3 se declaran **no aplicables**.

## 6. Umbral y procedimiento estadístico

- **τ se fija en Cal, para cada modelo por separado**, como la **mayor** puntuación que deja FNR ≤ 1 % en Cal. Después se aplica sin cambios a T.
- **Bootstrap pareado por clúster:** 2.000 réplicas, remuestreando **documentos** (sentencias del CENDOJ y documentos sintéticos) con reemplazo y conservando todas las instancias de cada documento. Los dos modelos se comparan sobre las mismas réplicas. Intervalo percentil bilateral al 95 %.
- **Cota de Clopper-Pearson** unilateral al 95 % para la FNR.

## 7. Criterios de éxito (Nivel 1, sobre T)

| Criterio | Pasa | No concluyente | No pasa |
|---|---|---|---|
| **C1** · % FP eliminados (TNR) del candidato a su τ | cota inferior del IC 95 % ≥ 25 % | punto ≥ 25 % y cota inferior < 25 % | punto < 25 % |
| **C2** · FNR del candidato a su τ (T con ≥ 500 positivos) | punto ≤ 1 % **y** cota superior CP ≤ 2,5 % | punto ≤ 1 % y CP > 2,5 % | punto > 1 % |
| **C3** · Δ = TNR(candidato) − TNR(LR), cada uno a su τ | Δ ≥ 5 puntos **y** cota inferior del IC pareado > 0 | Δ ≥ 5 y cota inferior ≤ 0 | Δ < 5 |

Si T tiene menos de 500 positivos, C2 se declara **no concluyente** sea cual sea el resultado.

**Cálculo del tamaño muestral para C2** (`tools/tamano_muestral.py`; cota superior unilateral al 95 % según el número de falsos descartes *k* en *n* positivos):

| n positivos | k = 0 | k = 1 | k = 2 | k = 3 | k = 5 | k = 7 |
|---|---|---|---|---|---|---|
| 100 | 2,95 % | 4,66 % | 6,16 % | 7,57 % | 10,23 % | 12,75 % |
| 300 | 0,99 % | 1,57 % | 2,08 % | 2,56 % | 3,47 % | 4,34 % |
| 500 | 0,60 % | 0,95 % | 1,25 % | 1,54 % | 2,09 % | 2,61 % |
| 700 | 0,43 % | 0,68 % | 0,90 % | 1,10 % | 1,50 % | 1,87 % |

Con 500 positivos, C2 pasa con 5 falsos descartes o menos. Con 0 falsos descartes, afirmar «≤ 1 %» exigiría 299 positivos (regla del tres), y «≤ 2,5 %» exigiría 119.

**Veredicto global:** la prueba de concepto **confirma** su pregunta solo si los tres criterios «pasan».

## 8. Nivel 2 · CENDOJ descriptivo (sin veredicto)

Solo sobre las instancias de CENDOJ de T:

- FNR puntual con su cota CP.
- % FP eliminados con IC por bootstrap de documento.
- Curva riesgo–cobertura: TNR cuando τ se fija en Cal para FNR ≤ ε, con ε ∈ {1, 2, 5} %.
- Todo desglosado por `rol` (parte / profesional / judicial / otro) y por jurisdicción.

## 9. Análisis exploratorios (sin umbral ni veredicto)

*Estos cortes motivan preguntas posteriores; no las demuestran ni las refutan.*

- **Cambio de fuente:** τ fijado solo con sintéticos y medido en CENDOJ.
- **Detector no visto:** candidatos de Presidio sobre las sentencias de T.
- **Jurisdicción cruzada:** τ fijado en Cal ∩ {civil, social} y medido en T ∩ {penal, contencioso}, y al revés.
- **Ablaciones** (3 semillas cada una): sin token de mayúscula; solo el candidato; solo el contexto; entrenamiento sin CENDOJ.
- **Curva de aprendizaje:** 25 %, 50 % y 100 % del entrenamiento.
- **Techo:** `PlanTL-GOB-ES/roberta-base-bne`, mismos hiperparámetros y 3 semillas.
- **Sonda de dominio:** AUC de una LR que distingue contexto sintético de CENDOJ. Si supera 0,9, el informe lo destaca como posible atajo.
- **Cuantización:** caída de TNR y FNR de FP32 a INT8; tamaño en MB; latencia p50 y p95 en CPU (i7-7700HQ, 4 hilos, lotes de 32, 10 lotes de calentamiento y 50 de medida).

## 10. Lo que esta prueba de concepto NO demuestra

- Que el resultado se mantenga en documentos **sin disociar** ni en otros tipos documentales (contratos, escrituras, expedientes).
- Ninguna **garantía estadística** de riesgo en producción: τ se fija en una muestra y no asegura nada fuera de ella.
- **Robustez** frente a detectores, fuentes o jurisdicciones no vistos (solo se explora, §9).
- La **validez jurídica** de la etiqueta: la anota una sola persona sin formación jurídica acreditada; el κ mide consistencia, no corrección.
- Nada sobre **identificación indirecta** por combinación de datos.

## 11. Cambios tras el preregistro

Todo cambio posterior al tag `preregistro` se registra en la bitácora, en el apartado «Desviaciones del protocolo», con fecha, motivo y efecto esperado. El informe final enumera todas las desviaciones.

## 12. Reproducibilidad

- Código, configuración y semillas en el repositorio.
- Versiones de Colab en `reports/entorno-colab.txt`.
- Predicciones por instancia en `reports/predicciones/`.
- Manifiesto de particiones con los identificadores de las sentencias (ROJ) y los hashes de sus textos.
- Criterio: con la misma semilla se obtienen las mismas predicciones al reexportar en CPU; la variabilidad entre semillas se reporta.
