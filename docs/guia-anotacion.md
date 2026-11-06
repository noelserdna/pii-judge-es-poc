# Guía de anotación

!!! warning "Versión 0 · borrador"
    Esta es la versión de trabajo. La versión 1 se cierra con el tag `guia-v1` **antes** de anotar ninguna instancia de los conjuntos de calibración o test. Todos los ejemplos de esta guía son **inventados**; ninguno procede de una resolución real.

## 1. Qué se anota

Cada **instancia** es una mención (el *span*) dentro de un fragmento de texto de unos 400 caracteres. El span aparece marcado así: `⟦span⟧`. Hay que responder **una sola pregunta**:

> **Si este documento NO estuviera disociado, ¿este span identificaría, o contribuiría directamente a identificar, a una persona física concreta?**

Es la **regla contrafactual** ([ADR-010](decisiones/ADR-010-etiqueta-cendoj.md)). Las sentencias del CENDOJ ya han sustituido los nombres reales por otros ficticios; hay que juzgar el **papel** que cumple el span, no si el nombre concreto es real.

## 2. Etiquetas

| Etiqueta | Cuándo |
|---|---|
| `SI` | El span es o forma parte de un dato que identifica a una persona física: su nombre (aunque sea un pseudónimo), un identificador personal, su domicilio, su teléfono o correo personal. |
| `NO` | El span no se refiere a una persona física o no la identifica: organismos, empresas, leyes, ciudades mencionadas de forma genérica, números de procedimiento, datos de contacto del juzgado, palabras sueltas mal detectadas. |
| `AMBIGUO` | Con los ±200 caracteres de contexto **no se puede decidir**. Debe ser excepcional (objetivo: < 5 %). No es un cajón para casos difíciles: si se puede decidir con una lectura atenta, se decide. |
| `EXCLUIDO_PLACEHOLDER` | El span es un marcador de disociación (`NUM000`, `DIRECCION001`, `CALLE000`…). |

Además de la etiqueta:

- **`categoria`**, solo si la etiqueta es `SI`: `PERSONA`, `IDENTIFICADOR`, `DIRECCION`, `CONTACTO`, `OTRO`.
- **`rol`**, solo si la etiqueta es `SI` y la categoría es `PERSONA`: `parte` (demandante, acusado, testigo, víctima, familiares…), `profesional` (procurador, letrado, perito, notario, graduado social…), `judicial` (magistrado, juez, LAJ, fiscal) u `otro`.
- **`nota`**, opcional: una línea si la decisión no es obvia.

## 3. Reglas

1. **Pseudónimos → `SI`.** «Teodosio» puesto por el CENDOJ en lugar del nombre real sigue cumpliendo el papel de nombre de una persona.
2. **Profesionales y miembros del tribunal → `SI`**, con su `rol`. Son personas identificadas, aunque en la práctica no se tapen. Si hay que taparlos es una cuestión de política, no de esta etiqueta.
3. **Tratamientos.** «Sr.», «Dña.», «D.» o «Magistrada» **solos**, sin nombre → `NO`. Si el span es «Sra. Agustina» → `SI`.
4. **Spans mal cortados.** Si contiene una parte reconocible del nombre de una persona → `SI`. Si no contiene ninguna → `NO`. Ejemplo: `⟦FERNANDEZ DON JAVIER⟧` en una lista de magistrados es `SI`; `⟦DEMANDADA DE⟧` es `NO`.
5. **Datos del órgano judicial → `NO`.** Teléfono, fax, correo, dirección o cuenta de consignaciones del juzgado.
6. **Empresas y organismos → `NO`**, aunque lleven un apellido. Excepción: si el contexto deja claro que se trata de un empresario individual identificado por ese nombre, `SI`.
7. **Lugares.**
    - Una ciudad o provincia mencionada de forma genérica («el Juzgado de Valladolid», «viajaron a Vitoria») → `NO`.
    - Un **domicilio** o una dirección concreta de una persona (calle y número, «la vivienda de la calle…») → `SI`, categoría `DIRECCION`.
    - Una localidad pequeña ligada a una persona concreta: si con el contexto puede contribuir a identificarla → `SI`, categoría `OTRO`; si no, `NO`. En caso de duda real, `AMBIGUO`.
8. **Números.** Números de procedimiento, recurso, sentencia o ley, fechas e importes → `NO`. DNI, NIE, pasaporte, NUSS, IBAN personal o matrícula de una persona → `SI`, categoría `IDENTIFICADOR`.
9. **Nombres de personas en citas de jurisprudencia o doctrina** («como dijo el ponente X en la STS…») → `SI`, `rol = judicial` u `otro`.
10. **Palabras corrientes detectadas como nombre** («FALLAMOS», «Acordaron», «estenotipia») → `NO`.

## 4. Ejemplos (inventados)

| Fragmento | Etiqueta | Categoría / rol |
|---|---|---|
| «…la vivienda que ocupaba ⟦Doña Eulalia⟧ desde 2019…» | `SI` | PERSONA / parte |
| «…representada por el Procurador ⟦D. Ramiro Ortega Vidal⟧ y asistida…» | `SI` | PERSONA / profesional |
| «…el ⟦Juzgado de Primera Instancia⟧ nº 4 de Soria dictó sentencia…» | `NO` | — |
| «…interpuesto el recurso de apelación ⟦312/2024⟧ ante esta Sala…» | `NO` | — |
| «…Teléfono: ⟦975 000 111⟧ Correo electrónico: sala.civil@…» (cabecera del juzgado) | `NO` | — |
| «…el acusado, con DNI ⟦12345678Z⟧, reconoció los hechos…» | `SI` | IDENTIFICADOR |
| «…se trasladaron desde ⟦Cuenca⟧ hasta Madrid para la vista…» | `NO` | — |
| «…era la única veterinaria de ⟦Villar del Humo⟧, donde residía con su madre…» | `SI` | OTRO |
| «…en el domicilio sito en ⟦calle Almendro 14⟧, 2º B…» | `SI` | DIRECCION |
| «…con domicilio en ⟦DIRECCION000⟧…» | `EXCLUIDO_PLACEHOLDER` | — |
| «…por todo lo expuesto, ⟦FALLAMOS⟧: estimar el recurso…» | `NO` | — |

## 5. Procedimiento

1. Abrir el CSV de anotación (`id, contexto, etiqueta, categoria, rol, nota`). El contexto ya trae el span marcado con `⟦ ⟧`.
2. Leer el fragmento completo antes de decidir.
3. Anotar como mucho **90 minutos seguidos**; descansar 10 minutos.
4. Registrar en `horas.csv` las horas y el número de instancias anotadas por sesión.
5. Las dudas que se repitan se anotan en la bitácora. Si obligan a cambiar una regla **antes** de `guia-v1`, se cambia aquí. **Después** de `guia-v1`, el cambio es una desviación del protocolo.
