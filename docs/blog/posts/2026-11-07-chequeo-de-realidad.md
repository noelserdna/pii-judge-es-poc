---
date: 2026-11-07
categories:
  - Paso 0
  - Datos
---

# Paso 0b · El chequeo de realidad cambia el plan

Antes de fijar ningún umbral, hemos pasado un detector sencillo por diez sentencias reales para ver qué sale. En una hora de lectura salieron tres sorpresas y una condición legal que obligan a corregir el plan. Este es justo el motivo de hacer el chequeo **antes** del preregistro.

<!-- more -->

## Qué se hizo

- **Infraestructura:** la clave de firma ya está registrada en GitHub y los commits aparecen como *Verified*. Zenodo queda conectado al repositorio: cada Release recibirá un DOI.
- **Aviso legal del CENDOJ:** se leyó antes de descargar nada. Ver «Qué se aprendió».
- **Selección de 10 sentencias de 2025**, en español, repartidas por jurisdicción: 3 civiles y 3 penales de Audiencias Provinciales, 2 sociales y 2 contencioso-administrativas de Tribunales Superiores de Justicia. Se descargaron una a una, con pausas, a una carpeta que nunca se sube al repositorio.
- **Detector v0** (`tools/chequeo_realidad.py`): expresiones regulares para DNI/NIE, teléfono, correo, IBAN y números con forma de expediente; una heurística para nombres precedidos de «D.», «Dña.», «Sr.»…; y el reconocedor de entidades de spaCy (`es_core_news_lg`) para personas, lugares y organizaciones.
- **Revisión manual en local de una muestra aleatoria de 120 candidatos**, para estimar cuántos son de verdad datos personales.

## Cifras

Las cifras completas, sin ningún texto, están en [`reports/chequeo-realidad.json`](https://github.com/noelserdna/pii-judge-es-poc/blob/main/reports/chequeo-realidad.json).

| | Valor |
|---|---|
| Sentencias | 10 (civil 3 · penal 3 · social 2 · contencioso 2) |
| Candidatos (menciones) | **2.881**, unos 290 por sentencia |
| Grupos distintos (documento + forma + etiqueta) | **1.302** |
| Grupos con una sola mención | 972 (75 %) |
| Repeticiones máximas de un mismo grupo | 201 |
| Candidatos por etiqueta del detector | personas 1.143 · organizaciones 661 · números tipo expediente 528 · lugares 526 · teléfonos 11 · correos 6 · IBAN 2 |
| Positivos estimados en la muestra de 120 | ~42 (≈ 35 %) |

## Qué se aprendió

1. **El volumen era el triple de lo previsto.** Con ~290 candidatos por sentencia, «anotar el 100 % de 20–25 sentencias» suponía 6.000–7.000 candidatos: imposible en 20 horas.
2. **Los positivos no escasean, pero se repiten.** La revisión escéptica del plan temía que en sentencias disociadas casi no hubiera datos personales verdaderos. Hay muchos (≈ 35 % de las menciones), pero concentrados en pocas personas: el pseudónimo del protagonista de una sentencia aparece más de 200 veces. Si se cuentan todas las menciones, una sola sentencia domina el resultado y las cotas estadísticas, que suponen observaciones independientes, salen engañosamente estrechas. → [ADR-012](../../decisiones/ADR-012-unidad-de-anotacion.md): se anota **una mención al azar por grupo**, con un máximo de 70 grupos por sentencia.
3. **Los identificadores que encuentra el detector son todos del juzgado.** Los 11 teléfonos, los 6 correos y los 2 IBAN son los datos de contacto del órgano y la cuenta de consignaciones, y esa cuenta se repite en varias sentencias. Son falsos positivos «de libro», perfectos para enseñar al validador que no todo número con forma de identificador es personal. Los positivos de tipo identificador solo podrán venir de los datos sintéticos, como ya preveía el plan.
4. **La disociación no es perfecta.** Al menos un domicilio de una parte quedó sin tapar. Es un recordatorio de por qué no se publica ningún texto ni contexto de estas sentencias, aunque sean públicas.
5. **El detector se equivoca de formas muy variadas.** Clasifica nombres de persona como lugares, palabras como «FALLAMOS» como personas, y corta mal los nombres en las listas de magistrados. La guía de anotación ya tiene reglas para eso ([ADR-010](../../decisiones/ADR-010-etiqueta-cendoj.md)).
6. **El aviso legal del CENDOJ** permite consultar las resoluciones para uso particular, pero exige su procedimiento de reutilización para **elaborar bases de datos**. El chequeo, procesado en local y publicado solo como cifras agregadas, se considera consulta. El Paso 3 sí construye un conjunto anotado, así que queda **condicionado a pedir y obtener esa autorización** ([ADR-013](../../decisiones/ADR-013-autorizacion-cendoj.md)).

## Decisiones

- [ADR-010](../../decisiones/ADR-010-etiqueta-cendoj.md) pasa de «propuesta» a **aceptada**, con reglas añadidas para spans mal cortados.
- [ADR-012](../../decisiones/ADR-012-unidad-de-anotacion.md): unidad de anotación = una mención por grupo; muestreo de hasta 70 grupos por sentencia.
- [ADR-013](../../decisiones/ADR-013-autorizacion-cendoj.md): el Paso 3a queda bloqueado hasta tener la autorización de reutilización del CENDOJ, con un plan B si no llega.

## Desviaciones del protocolo

No aplica: el protocolo todavía no está cerrado. Precisamente por eso estos cambios se incorporan **antes** del preregistro y no cuentan como desviación.

## Siguiente paso

- Solicitar al CENDOJ la autorización de reutilización (la presenta el autor).
- Paso 0c: redactar el protocolo con estas cifras (cálculo muestral, unidad de anotación, criterios C1–C3) y la guía de anotación v0. Después, el tag `preregistro`, la Release y el DOI.

## Horas

5 h (chequeo 4 h · infraestructura 1 h).

## Enlaces

- Issue del paso: [#1](https://github.com/noelserdna/pii-judge-es-poc/issues/1)
- Script: [`tools/chequeo_realidad.py`](https://github.com/noelserdna/pii-judge-es-poc/blob/main/tools/chequeo_realidad.py)
