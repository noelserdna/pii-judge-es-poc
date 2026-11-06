# ADR-001 · Prueba de concepto exploratoria, independiente y con fondos propios

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí: el protocolo y la delimitación sirven de antecedente.

## Contexto
Antes de plantear cualquier desarrollo mayor hace falta saber si la idea (un validador pequeño que juzga en contexto los candidatos de los detectores) tiene algún recorrido experimental. No existe hoy ningún experimento, solo un concepto documentado.

## Decisión
Hacer una prueba de concepto **pequeña, cerrada y fechada**, con fondos y tiempo propios, que responda a una única pregunta fijada por escrito antes de experimentar. Al cerrar, el repositorio se archiva. Cualquier trabajo posterior se documenta aparte y cita este como antecedente.

## Alternativas descartadas
- **No hacer nada experimental antes de un desarrollo mayor.** Sin ningún dato no hay forma de dimensionar nada (cuántos positivos hacen falta, si la etiqueta es anotable, qué falsos positivos produce un detector real).
- **Una prueba abierta, sin fecha de cierre.** Se confundiría con el desarrollo posterior y no serviría como evidencia de un trabajo acotado.

## Consecuencias
- Alcance mínimo: una pregunta, un modelo candidato, dos baselines, un conjunto de datos público.
- Lo que la prueba no demuestra se declara explícitamente en el protocolo, el README y el informe.
- Las horas y los costes se registran desde el primer día (`horas.csv`, `costes.csv`).
