# Fuentes y licencia del corpus sintético

- **Plantillas** (`src/data/synth.py`): 12 familias de documentos de estilo judicial escritas a mano por el autor. Son textos inventados: ningún hecho, nombre ni número corresponde a un caso real.
- **Listas de valores** (`src/data/gazetteers.py`): nombres de pila y apellidos frecuentes en España, nombres de municipios y de localidades pequeñas, nombres de vías (árboles y flores) y oficios, todos escritos a mano. Son datos de hecho de uso común, sin autoría protegible. Cada nombre completo se forma combinando al azar un nombre y dos apellidos, así que no se refiere a ninguna persona concreta.
- **Identificadores**: los DNI, NIE e IBAN se generan al azar con dígitos de control válidos, salvo un 15 % de DNI con la letra errónea a propósito. Teléfonos y correos inventados. Cualquier coincidencia con un identificador real es casual.

Ficheros:

| Fichero | Contenido |
|---|---|
| `documentos.jsonl` | Un documento por línea: `doc_id`, `familia`, `particion`, `texto` y `huecos` (posición, tipo, etiqueta, categoría y rol de cada dato insertado) |
| `candidatos.jsonl` | Candidatos del detector con su etiqueta heredada del hueco con el que se solapan (`fuente = hueco`) o `NO` si caen en texto fijo de la plantilla (`fuente = plantilla`) |
| `resumen.json` | Recuentos por partición y sensibilidad del detector sobre los datos personales insertados |

Se regenera con: `uv run --group detector python -m src.data.synth --salida data/synth` (semilla 20261107).

Licencia: **CC BY 4.0** (ver `LICENSE-docs`).
