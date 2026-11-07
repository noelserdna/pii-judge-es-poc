# ADR-017 · Diseño del corpus sintético

**Estado:** aceptada · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: el generador y su forma de etiquetar.

## Contexto
El protocolo (§3.1) pide 10–12 familias de plantillas con pares contrastivos, particiones por familia, listas de valores disjuntas entre particiones y unos mínimos de positivos: al menos 300 en calibración y 450 en test. Quedaba por decidir qué es una «familia» y cómo se etiquetan los candidatos que el detector encuentra en el texto fijo de las plantillas.

## Decisión
- **Familia = tipo de documento:** desahucio, despido, tráfico, familia, honor, herencia, contencioso, lesiones, reclamación, menores, seguros y extranjería. Cada familia tiene su cabecera, sus frases y su cierre. Todas usan los mismos **tipos de dato**, pero en contextos que se contraponen:
    - el DNI o el IBAN de una parte frente al número de expediente o la cuenta del juzgado;
    - el teléfono o el correo personal frente a los del órgano;
    - el domicilio de una persona frente a la sede de un organismo;
    - un pueblo que identifica a alguien («la única veterinaria de…») frente a una ciudad citada de pasada.
- **Particiones:** 7 familias para entrenamiento, 2 para calibración (lesiones y reclamación) y 3 para test (menores, seguros y extranjería). El test mide la generalización a **estructuras de documento no vistas**, no a tipos de dato nuevos.
- **Listas de valores** partidas 60/20/20 de forma determinista, sin ninguna cadena compartida entre listas (se quitaron «Zamora», «Toledo» y «Castaño», que eran a la vez apellido y municipio o vía).
- **Concordancia de género** entre el tratamiento y el nombre («Dña.» con nombre femenino), para no regalar al modelo un atajo que distinga lo sintético de lo real.
- **Etiquetado:**
    - un candidato hereda la etiqueta del hueco con el que se solapa; si se solapa con varios y alguno es `SI`, gana `SI` (regla 4 de la guía);
    - un candidato que cae en texto fijo es `NO`, porque las plantillas no contienen datos personales.

    El protocolo preveía excluir los candidatos sin hueco; se etiquetan `NO` porque, por construcción, lo son. Se registra como **desviación D4**.
- Se genera hasta superar los mínimos: entrenamiento ≥ 1.000 positivos, calibración ≥ 320 y test ≥ 480, con semilla 20261107.

## Alternativas descartadas
- **Familia = tipo de dato** (una familia para DNI frente a expediente, otra para teléfono personal frente al del órgano…). El test tendría tipos de dato que el modelo nunca ha visto, y C2 fallaría por diseño, no por falta de capacidad.
- **Excluir los candidatos del texto fijo.** Se perderían justo los falsos positivos más parecidos a los reales («Dña», «Magistrada», «Juzgado»).

## Consecuencias
- Resultado: 313 documentos y 4.563 candidatos; positivos: entrenamiento 1.003, calibración 322 y test 483. El detector ve el 96,8 % de los datos personales insertados; los que no ve son sobre todo oficios («veterinaria»), que el detector no busca.
- Los positivos son el ~40 % de los candidatos, frente al 15–20 % del CENDOJ. La sonda de dominio (§9 del protocolo) lo tendrá en cuenta.
- El corpus se publica completo (`data/synth/`, CC BY 4.0).
