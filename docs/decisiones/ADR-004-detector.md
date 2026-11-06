# ADR-004 · Detector propio para entrenar y evaluar; Presidio solo en test como detector no visto

**Estado:** aceptada · **Fecha:** 2026-11-06 · **¿Se reutilizaría en trabajos posteriores?** Sí: la política de solapamiento y el formato de candidato.

## Contexto
El validador juzga candidatos que produce un detector. El detector no es el objeto de estudio, pero determina qué falsos positivos verá el validador. Tres opciones: un detector propio (regex + NER de spaCy), Presidio (Microsoft, software libre, con reconocedores para español) o ambos.

## Decisión
- **Detector propio** (`src/detector/`): expresiones regulares deliberadamente sensibles (DNI/NIE con y sin checksum válido, teléfonos, correos, IBAN, patrones de expediente) + NER de spaCy `es_core_news_lg` (PER, LOC, ORG) + heurística de mayúscula tras «D.», «Dña.», «calle». Produce los candidatos de entrenamiento, calibración y test.
- **Presidio Analyzer** se ejecuta **solo sobre los documentos de test del CENDOJ**, para medir qué pasa cuando el validador recibe candidatos de un detector que no vio en entrenamiento. Resultado exploratorio, sin veredicto.
- Política de solapamiento: los spans que se solapan se fusionan en un candidato (se conserva el más largo) y los campos `detector` y `det_label` son listas.

## Alternativas descartadas
- **Presidio como detector principal.** Añade configuración sin cambiar la pregunta, y perder el control sobre la ambigüedad del detector quita la posibilidad de generar falsos positivos a propósito.
- **Solo detector propio.** Con dos horas más se obtiene un eje de «detector no visto» que de otro modo no existiría.

## Consecuencias
- Los falsos positivos de entrenamiento son, en parte, los que el autor diseñó. La sonda sintético-vs-real y las ablaciones (ver protocolo) sirven para detectar si el modelo aprende atajos.
- Los candidatos que solo produce Presidio en test también se anotan (tope de dos horas).
