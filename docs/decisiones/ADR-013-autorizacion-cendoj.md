# ADR-013 · El uso del CENDOJ más allá del chequeo queda condicionado a su autorización de reutilización

**Estado:** aceptada · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: cualquier uso del CENDOJ para construir conjuntos de datos.

## Contexto
El aviso legal del buscador del CENDOJ, leído antes de descargar nada, dice en esencia tres cosas:

- se pueden consultar las resoluciones **para uso particular**;
- no se permite el uso comercial **ni la descarga masiva**;
- **la reutilización para elaborar bases de datos** o con fines comerciales debe seguir el procedimiento y las condiciones que fija el CGPJ a través del CENDOJ.

El plan preveía «revisar el aviso legal» pero no contaba con esta última condición. Anotar ~25 sentencias y publicar un manifiesto y anotaciones por posiciones es, de hecho, elaborar una base de datos a partir de ellas.

## Decisión
- **Chequeo de realidad (Paso 0b):** 10 sentencias, descargadas una a una con pausas, leídas y procesadas **solo en local**. Lo único que se publica son cifras agregadas (recuentos y hashes; ningún texto). Se considera uso particular de consulta.
- **Se solicita al CENDOJ la autorización de reutilización** para el uso previsto en el Paso 3 (anotación de ~25 resoluciones y publicación de identificadores, hashes y posiciones sin texto, con fines de investigación).
- **El Paso 3a (CENDOJ) queda bloqueado** hasta tener respuesta. Los pasos que no dependen del CENDOJ (guía, detector, sintéticos) siguen adelante.
- **Plan B**, si la autorización no llega o se deniega: un ADR nuevo que sustituye la fuente real. Se evaluarán fuentes jurídicas con licencia abierta explícita. Mientras tanto, el criterio C2 podría evaluarse solo sobre sintéticos y el CENDOJ quedaría como chequeo descriptivo de 10 sentencias, lo que se declararía como desviación del protocolo.

## Alternativas descartadas
- **Seguir con el plan original interpretando todo como uso particular.** No encaja con la letra del aviso cuando se publica un conjunto anotado.
- **Abandonar el CENDOJ desde ya.** Se perdería la única fuente de texto jurídico real y disociado sin haber preguntado siquiera.

## Consecuencias
- El calendario del Paso 3 depende de un tercero. Se registra la fecha de la solicitud y la de la respuesta en la bitácora.
- Las 10 sentencias del chequeo no se reutilizan como conjunto anotado salvo que la autorización lo cubra.
