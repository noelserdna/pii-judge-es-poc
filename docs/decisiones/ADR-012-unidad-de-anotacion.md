# ADR-012 · Unidad de anotación: una mención por grupo y muestreo por documento

**Estado:** aceptada · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: el diseño de la unidad de anotación y evaluación.

## Contexto
El chequeo de realidad (Paso 0b, 10 sentencias, `reports/chequeo-realidad.json`) dio tres cifras que el plan no había previsto:

- El detector v0 produce **~290 candidatos por sentencia** (2.881 en 10). Con las 20–25 sentencias previstas serían 6.000–7.000, el triple de lo que cabe en 20 h de anotación.
- Las menciones **se repiten mucho**: las 2.881 se reducen a **1.302 grupos** (mismo documento, misma forma normalizada, misma etiqueta del detector). Un mismo pseudónimo aparece más de 200 veces en una sentencia; tres de cada cuatro grupos tienen una sola mención.
- Las menciones repetidas de una misma persona **no son observaciones independientes**: si se cuentan todas, una sola sentencia con un protagonista muy citado domina la métrica y las cotas estadísticas (que suponen independencia) salen falsamente estrechas.

## Decisión
- **Grupo** = (documento, forma normalizada del span, etiqueta del detector). La normalización quita mayúsculas, tratamientos («Sr.», «Dña.», «D.») y puntuación de los extremos.
- **Instancia de anotación y de evaluación** = **una mención elegida al azar de cada grupo** (semilla fija), con su contexto de ±200 caracteres. Se anota esa mención, no el grupo en abstracto.
- **Muestreo por documento:** de cada sentencia se toma una muestra aleatoria **estratificada por etiqueta del detector** de, como máximo, **70 grupos**. Así caben **~25 sentencias** en el presupuesto de anotación (~1.700 instancias) y el conjunto de test tiene unas 10 sentencias, suficientes para un bootstrap por documento.
- **Entrenamiento:** en las sentencias de la partición de entrenamiento (y solo ahí), la etiqueta de la mención anotada **se propaga** al resto de menciones del mismo grupo. Los conflictos se marcan y se excluyen.
- **Calibración y test:** solo la mención anotada de cada grupo. Ninguna propagación.
- Las métricas se calculan por instancia y los intervalos se obtienen por **bootstrap por documento**.

## Alternativas descartadas
- **Anotar el 100 % de las menciones de pocas sentencias.** Con ~8 sentencias el test tendría 3: el bootstrap por documento no tendría sentido.
- **Anotar el 100 % de los grupos de ~12 sentencias.** Mejor, pero el test quedaría en ~5 sentencias de solo 4 jurisdicciones.
- **Evaluar todas las menciones con la etiqueta propagada.** Infla los positivos con repeticiones de la misma persona y viola la independencia que suponen Clopper-Pearson y el bootstrap por instancia.

## Consecuencias
- Cambia la estimación del Paso 3: «anotar el 100 % de los candidatos de 20–25 sentencias» pasa a ser «anotar hasta 70 grupos por sentencia en ~25 sentencias».
- Con la tasa de positivos observada en el chequeo (≈35 % por mención, que se espera algo menor por grupo), el CENDOJ aportaría ~150 positivos al test, que con los ≥ 450 sintéticos superan los 500 que exige el criterio C2.
- Se publican en el manifiesto el identificador del grupo y la posición de la mención anotada (sin texto), para que el muestreo sea reproducible.
