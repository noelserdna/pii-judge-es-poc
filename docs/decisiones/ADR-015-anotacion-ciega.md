# ADR-015 · Toda la anotación se hace en modo ciego

**Estado:** aceptada · **Fecha:** 2026-11-07 · **¿Se reutilizaría en trabajos posteriores?** Sí: cualquier anotación con sugerencias automáticas.

## Contexto
Para anotar se construyó un anotador web local (`tools/anotador/`) que puede mostrar una sugerencia de etiqueta hecha por una IA. Hay dos modos:

- **Revisión:** la sugerencia aparece ya rellenada y la persona la acepta o la cambia.
- **Ciego:** la persona elige primero; la sugerencia se muestra después y la herramienta guarda la primera elección.

En la prueba en seco con las sentencias del chequeo, que quedan fuera de calibración y test:

| | Revisión (60 instancias) | Ciego (30 instancias nuevas) |
|---|---|---|
| Mediana por instancia | 3,6 s | 4,6 s |
| Acuerdo con la IA | 60 de 60 (100 %) | 96,7 % · κ = 0,91 |
| Cambios tras ver la sugerencia | — | 0 |

Aceptar el 100 % de las sugerencias en menos de 4 segundos es la firma del **sesgo de automatización**: la etiqueta deja de ser un juicio humano. El modo ciego cuesta solo ~1 s más por instancia y produce etiquetas propias.

## Decisión
- **Todas las instancias del Paso 3** (entrenamiento, calibración y test) se anotan en **modo ciego**.
- La sugerencia de la IA se usa solo como **control a posteriori**: si después de verla se cambia la etiqueta, el cambio queda registrado, porque se guarda la primera elección.
- Se reportan tres cifras: el acuerdo de la primera elección con la IA, el acuerdo final y el número de cambios.
- La etiqueta oficial es la **final** del anotador humano.

## Alternativas descartadas
- **Todo en modo revisión.** Las etiquetas pasarían a ser «IA revisada por un humano», en contra de lo que dice el protocolo.
- **Modo mixto** (ciego en calibración y test, revisión en entrenamiento). Se eligió en un primer momento para ahorrar tiempo, pero la prueba ciega mostró que el ahorro sería de unos 17 minutos en total. No compensa tener etiquetas de entrenamiento ancladas.
- **Sin ninguna sugerencia.** Se pierde un control barato y la medida de cuántas veces se cambia de opinión.

## Consecuencias
- No hay desviación del protocolo, porque la etiqueta sigue siendo humana.
- Estimación para el Paso 3: ~1.700 instancias a ~5–8 s, entre 2,5 y 4 horas de anotación pura, muy por debajo de las 18 h presupuestadas.
- Las sugerencias de la IA para el Paso 3 tienen que generarse **antes** de anotar y guardarse aparte, para que no se puedan ajustar después.
- La IA que sugiere es la misma familia de modelos que podría usarse como baseline o como juez en trabajos posteriores. Eso se declara en el informe.

## Seguimiento
- **7-11-2026:** para la anotación principal (1.642 instancias del CENDOJ) **no se generan sugerencias**. Escribir a mano 1.642 sugerencias de la IA no es viable. Usar las de un modelo entrenado en este mismo proyecto introduciría su sesgo en las etiquetas, justo el problema que este ADR quería evitar. Se anota en **modo ciego puro**. El control de consistencia lo da la re-anotación a ciegas de 100 instancias al menos 7 días después (protocolo §4).
