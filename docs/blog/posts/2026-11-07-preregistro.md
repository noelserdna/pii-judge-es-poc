---
date:
  created: 2026-11-07
  updated: 2026-11-07
categories:
  - Paso 0
  - Hito
---

# Paso 0c · Protocolo preregistrado: cierre del Paso 0

El protocolo está cerrado. Desde ahora la pregunta, los datos, las métricas y los umbrales de éxito están fijados con firma, fecha y una copia archivada que no depende de este repositorio. **Lo que salga a partir de aquí se medirá contra lo que hoy está escrito.**

<!-- more -->

## Qué se hizo

- **Protocolo v1** ([`docs/protocolo.md`](../../protocolo.md)), a partir del borrador v0 publicado el mismo día. Incorpora las cifras del chequeo de realidad:
    - una mención por grupo y hasta 70 grupos por sentencia;
    - el cálculo del tamaño muestral de C2;
    - la contingencia preregistrada si el CENDOJ no contesta antes del 24-11;
    - la exclusión de las 10 sentencias del chequeo de los conjuntos de calibración y test.
- **Tag firmado** `preregistro`, con el SHA-256 del protocolo en el mensaje.
- **Release de GitHub** [`preregistro`](https://github.com/noelserdna/pii-judge-es-poc/releases/tag/preregistro), con el protocolo adjunto.
- **DOI de Zenodo:** [10.5281/zenodo.24024318](https://doi.org/10.5281/zenodo.24024318).
- **Guía de anotación v0** publicada. La v1 se cierra en el Paso 1.
- **Capítulo 0 de la guía didáctica:** [Cómo se organiza un experimento honesto](../../guia/00-experimento-honesto.md), con la figura de la regla del tres generada por script.

## Cifras

| | |
|---|---|
| SHA-256 de `docs/protocolo.md` en el tag (finales de línea LF) | `0190bc4b7b328b9dc1f0915d4b03fa1540b69dbbbf2443c818c0ea632c884fff` |
| Horas acumuladas al cerrar el Paso 0 | 13,5 h (previstas: 12) |
| Coste | 0 € |

## Qué se aprendió

- **Una Release necesita un tag que ya exista con ese nombre.** El plan decía «Release `v0.1-preregistro`» sobre el tag `preregistro`, y `gh release create --verify-tag` lo rechazó con razón. Se creó la Release con el mismo nombre que el tag: hay una cosa menos que explicar.
- **El hash depende de los finales de línea.** En Windows el fichero de trabajo tiene CRLF y git guarda LF, así que el hash del fichero local no coincide con el del repositorio. El hash publicado es el del contenido guardado en git (`git show preregistro:docs/protocolo.md | sha256sum`), que es el que cualquiera puede reproducir.
- **Zenodo tarda unos segundos** en crear el registro a partir del webhook de la Release, y su buscador puede tardar algo más en mostrarlo.

## Desviaciones del protocolo

Ninguna: el protocolo acaba de cerrarse.

## Siguiente paso

**Paso 1 · Guía de anotación v1** ([#2](https://github.com/noelserdna/pii-judge-es-poc/issues/2)): anotar en seco unas decenas de instancias **sintéticas** para probar las reglas, ajustar la guía y cerrarla con el tag `guia-v1`. En paralelo, se espera la respuesta del CENDOJ.

## Horas

3 h.

## Enlaces

- Issue del paso: [#1](https://github.com/noelserdna/pii-judge-es-poc/issues/1) (se cierra con esta entrada)
- Release: [preregistro](https://github.com/noelserdna/pii-judge-es-poc/releases/tag/preregistro) · DOI: [10.5281/zenodo.24024318](https://doi.org/10.5281/zenodo.24024318)
