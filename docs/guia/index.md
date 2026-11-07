# Aprende

Esta sección explica, paso a paso, **qué se está haciendo y por qué**, para alguien que sabe programar pero no ha entrenado un modelo ni ha trabajado con protección de datos. Cada paso del proyecto tiene su capítulo, que se escribe **al terminar** ese paso: aquí no se enseña nada que no se haya hecho ya.

## Tres hilos para seguir

Cada capítulo marca sus conceptos con uno de estos iconos, para que puedas seguir solo el hilo que te interese:

| Icono | Hilo | De qué va |
|---|---|---|
| :brain: | **Crear un modelo** | datos → particiones → baselines → afinado → umbral → evaluación → cuantización |
| :lock: | **Proteger datos** | qué es un dato personal, identificabilidad, seudonimización frente a anonimización, por qué un texto «disociado» sigue mereciendo cuidado, qué cuesta un falso descarte |
| :hammer_and_wrench: | **Herramientas** | uv, git, `gh`, firma SSH, GitHub Actions, MkDocs, Zenodo, spaCy, Presidio, transformers, Colab, ONNX |

## Capítulos — 3 / 9

| Cap. | Título | Estado |
|---|---|---|
| 0 | [Cómo se organiza un experimento honesto](00-experimento-honesto.md) | 🟢 publicado |
| 1 | [¿Qué es un dato personal?](01-dato-personal.md) | 🟢 publicado |
| 2 | [Cómo se encuentran candidatos](02-encontrar-candidatos.md) | 🟢 publicado |
| 3 | Datos para enseñar y datos para examinar | ⚪ |
| 4 | Congelar antes de mirar | ⚪ |
| 5 | Lo mínimo contra lo que compararse | ⚪ |
| 6 | Afinar un encoder | ⚪ |
| 7 | Medir sin engañarse | ⚪ |
| 8 | Leer el resultado | ⚪ |
| — | [Glosario](glosario.md) | 🔵 crece con cada capítulo |

## Cómo está hecho cada capítulo

1. **¿Qué vamos a hacer y por qué?** En tres líneas y sin jerga.
2. **Conceptos clave.** Cada uno con una analogía cotidiana y, después, la definición precisa.
3. **Visual principal.** Un diagrama o una figura que muestre el mecanismo, no solo el resultado.
4. **Cómo se hace.** Los comandos y el código reales del repositorio, comentados.
5. **Errores típicos y cómo los evitamos.** Enlaza con lo aprendido en la bitácora.
6. **Compruébalo tú.** Tres preguntas con la respuesta escondida.
7. **Para profundizar.** Dos o tres enlaces a fuentes fiables.

!!! note "Sobre los ejemplos"
    Todos los fragmentos de texto que aparecen en la guía son **sintéticos**: están inventados para ilustrar. Nunca se reproducen fragmentos de resoluciones reales.
