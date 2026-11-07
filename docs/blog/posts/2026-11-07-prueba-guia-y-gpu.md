---
date: 2026-11-07
categories:
  - Paso 1
  - Paso 6
  - Herramientas
---

# Paso 1 · Prueba en seco de la guía, un anotador web y la GPU, medida

Tres cosas en una sesión: se probó la guía de anotación con 60 instancias, se construyó una herramienta para anotar que se lee bien y se midió qué se puede entrenar en el portátil. La conclusión más importante es **metodológica** y no técnica: cuando la máquina sugiere, la persona acepta.

<!-- more -->

## Qué se hizo

- **Muestreo por grupos** ([ADR-012](../../decisiones/ADR-012-unidad-de-anotacion.md)) en `src/annotate/muestreo.py`, con tests. Se extrajeron 60 instancias, 6 por sentencia del chequeo. Esas sentencias no entran en calibración ni en test.
- **Anotación previa hecha por la IA** con la guía v0. Destapó 4 huecos en las reglas, que se corrigieron en la **guía v0.1**: cargos sin nombre, spans con palabras de más, identificadores de resoluciones y fragmentos de fecha.
- **Anotador web local** (`tools/anotador/`): solo escucha en `127.0.0.1`, resalta el span, rellena la sugerencia, tiene atajos de teclado, mide el tiempo por instancia y ofrece dos modos, *revisión* y *ciego*. Se creó porque el CSV en Excel era ilegible.
- **Revisión humana** de las 60 instancias en modo revisión.
- **Prueba de humo de GPU** (`tools/gpu_humo.py`) con DistilBETO y RoBERTalex.

## Cifras

| Prueba de la guía | |
|---|---|
| Instancias | 60 (9 positivas · 51 negativas · 0 ambiguas) |
| Tiempo total del humano | 7,3 min (mediana **3,6 s** por instancia; las dos primeras, 121 y 75 s, fueron para aprender la herramienta) |
| Sugerencias aceptadas sin cambios | **60 de 60** |
| Positivos por grupo | 15 % (frente al ~35 % contando cada mención) |

| GPU (GTX 1060, 3 GB) | Ejemplos/s | Memoria máx. |
|---|---|---|
| DistilBETO, batch 32 | 40 | 2,1 GB |
| RoBERTalex, batch 8 | 16,5 | 2,4 GB |
| Inferencia DistilBETO en CPU, FP32 | 11 | — |

## Qué se aprendió

1. **60 de 60 aceptadas en 3,6 segundos de mediana no demuestra que la guía sea clara: demuestra que la sugerencia manda.** Es el llamado *sesgo de automatización*. Con la sugerencia delante, revisar se convierte en confirmar. El acuerdo de κ = 1,00 entre la IA y el humano no tiene valor como medida independiente. Para la anotación real, mostrar sugerencias convertiría la etiqueta en «lo que dijo la IA, con visto bueno». Además, la IA que sugiere es de la misma familia que podría actuar como baseline o como juez, lo que añade circularidad. → Hay que decidir el modo de anotación del Paso 3 (ver «Siguiente paso»).
2. **Contando grupos, los positivos bajan al 15 %.** Los nombres se repiten mucho y los negativos son muy variados. Además, muchos negativos son **triviales** (teléfonos del juzgado, números de sentencias citadas), así que el criterio C1 (eliminar al menos el 25 % de los falsos positivos) puede resultar fácil. No se cambia el protocolo, que ya está preregistrado: se anota aquí como riesgo y el informe lo discutirá.
3. **El portátil basta para entrenar.** PyTorch 2.14 con CUDA 12.6 sigue soportando esta GPU de 2016. DistilBETO cabe con el batch 32 del protocolo y cada corrida dura unos 6 minutos. FP16 no acelera nada en esta arquitectura. → [ADR-014](../../decisiones/ADR-014-computo-local.md): se entrena en local y **los contextos del CENDOJ nunca salen del ordenador**.
4. **El modelo de referencia del protocolo ya no existe.** `PlanTL-GOB-ES/roberta-base-bne` quedó sin pesos en Hugging Face en julio de 2025. Su sucesor jurídico oficial es `BSC-LT/RoBERTalex` (125M, cased, Apache-2.0).
5. **Una inferencia de 11 ejemplos por segundo en CPU (FP32) queda lejos de los «20 ms por candidato»** que planteaban las ideas iniciales del proyecto. No es un criterio de esta prueba, pero lo será la medida INT8 del análisis exploratorio.

## Desviaciones del protocolo

| # | Sección | Cambio | Motivo | Efecto esperado |
|---|---|---|---|---|
| D1 | §9 Techo | `PlanTL-GOB-ES/roberta-base-bne` → `BSC-LT/RoBERTalex` | El modelo previsto ya no tiene pesos publicados | Ninguno sobre C1–C3. La referencia pasa a ser del dominio jurídico, así que el techo podría salir más alto |
| D2 | §9 Techo | RoBERTalex con batch 8 y acumulación ×4 (efectivo 32) | No cabe batch 32 en 3 GB | Equivalente salvo por el *dropout* |
| D3 | §12 | `reports/entorno-colab.txt` → `reports/entorno.txt` | Se entrena en local ([ADR-014](../../decisiones/ADR-014-computo-local.md)) | Ninguno |

## Siguiente paso

**Decidir el modo de anotación del Paso 3** antes de cerrar `guia-v1`. Propuesta: una segunda prueba de 30 instancias nuevas en **modo ciego**, para medir el tiempo real sin sugerencia y el acuerdo de verdad entre la IA y el humano.

## Horas

2,5 h (prueba de la guía y anotador 1,5 h · GPU 1 h).

## Enlaces

- Issues: [#2](https://github.com/noelserdna/pii-judge-es-poc/issues/2) (Paso 1) · [#7](https://github.com/noelserdna/pii-judge-es-poc/issues/7) (Paso 6)
