# Glosario

Términos de los tres hilos de la guía. Crece con cada capítulo; cada término enlaza al capítulo donde se explica.

| Término | Hilo | Definición breve | Capítulo |
|---|---|---|---|
| Dato personal | :lock: | Cualquier información sobre una persona física identificada o identificable (art. 4.1 RGPD). | [1](01-dato-personal.md) |
| Disociación | :lock: | Sustituir los datos identificativos de un documento por otros ficticios o por marcadores; lo que hace el CENDOJ antes de publicar. No equivale a anonimización. | [1](01-dato-personal.md) |
| Falso positivo | :brain: | Un candidato que el detector marcó como dato personal y no lo es. | 2 |
| Falso descarte (falso negativo) | :brain: | Un dato personal verdadero que el validador descarta por error. La métrica crítica de este proyecto. | 7 |
| Preregistro | :brain: | Fijar por escrito, con fecha verificable, la pregunta y los criterios de éxito **antes** de ver los resultados. | [0](00-experimento-honesto.md) |
| Regla del tres | :brain: | Si en *n* intentos no observas ningún fallo, la tasa real de fallos está por debajo de 3/*n* con un 95 % de confianza. | [0](00-experimento-honesto.md) |
| Clopper-Pearson (cota de) | :brain: | Cálculo exacto del máximo plausible de una tasa de fallos a partir de *k* fallos observados en *n* intentos. La regla del tres es su caso particular con *k* = 0. | [0](00-experimento-honesto.md) |
| *p-hacking* | :brain: | Probar muchas formas de analizar los datos y contar solo la que sale bien. El preregistro lo impide. | [0](00-experimento-honesto.md) |
| Firma SSH de commits | :hammer_and_wrench: | Firma criptográfica que demuestra quién hizo un commit o un tag y que no ha cambiado desde entonces. GitHub la muestra como *Verified*. | [0](00-experimento-honesto.md) |
| DOI | :hammer_and_wrench: | Identificador permanente de un objeto digital (aquí, una versión archivada del repositorio en Zenodo), citable y con fecha que pone el archivo. | [0](00-experimento-honesto.md) |
| ADR | :hammer_and_wrench: | *Architecture Decision Record*: nota corta que registra una decisión, su contexto, las alternativas y sus consecuencias. | [0](00-experimento-honesto.md) |
| Seudonimización | :lock: | Sustituir identificadores para que el dato no se pueda atribuir a nadie sin información adicional. Sigue siendo dato personal (art. 4.5 RGPD). | [1](01-dato-personal.md) |
| Anonimización | :lock: | Que nadie, con medios razonables, pueda reidentificar a la persona. Exige evaluar el riesgo residual. | [1](01-dato-personal.md) |
| Cuasi-identificador | :lock: | Dato que por sí solo no identifica, pero combinado con otros sí (profesión + localidad pequeña). | [1](01-dato-personal.md) |
| Regla contrafactual | :lock: | En textos disociados, preguntar si el span identificaría a alguien **si el documento no estuviera disociado**. | [1](01-dato-personal.md) |
| κ de Cohen | :brain: | Acuerdo entre dos anotaciones descontando el acuerdo esperable por azar. | [1](01-dato-personal.md) |
| Sesgo de automatización | :brain: | Tendencia a confirmar lo que propone una máquina en lugar de juzgar por cuenta propia. | [1](01-dato-personal.md) |
