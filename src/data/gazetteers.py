"""Listas de valores para rellenar plantillas sintéticas, **disjuntas por partición**.

Son nombres y apellidos frecuentes en España, municipios y nombres de vía, escritos a
mano (ver data/synth/FUENTES.md). Ninguna combinación nombre + apellidos corresponde a
una persona concreta conocida; son datos inventados.

Cada lista se reparte de forma determinista en tres bloques disjuntos (train, cal, test)
para que el modelo no pueda acertar en test por haber visto el mismo nombre en train.
"""

from __future__ import annotations

NOMBRES_F = ["Adela", "Alba", "Alicia", "Amparo", "Ángela", "Aurora", "Blanca", "Carmen", "Celia", "Clara", "Diana", "Dolores", "Elena", "Encarna", "Esther", "Eva", "Fernanda", "Gloria", "Graciela", "Inés", "Irene", "Jacinta", "Josefa", "Laura", "Lidia", "Lucía", "Margarita", "Marta", "Mercedes", "Natalia", "Noelia", "Paloma", "Patricia", "Pilar", "Ramona", "Remedios", "Rocío", "Rosa", "Sara", "Silvia", "Teresa", "Valentina", "Virginia", "Yolanda"]

NOMBRES_M = ["Agustín", "Alberto", "Alfonso", "Andrés", "Antonio", "Benito", "Bruno", "Carlos", "César", "Cristóbal", "Diego", "Eduardo", "Emilio", "Enrique", "Eugenio", "Federico", "Fidel", "Gonzalo", "Gregorio", "Hilario", "Ignacio", "Isidro", "Jaime", "Julián", "Leandro", "Lorenzo", "Luis", "Marcelo", "Mario", "Matías", "Miguel", "Nicolás", "Óscar", "Pascual", "Pedro", "Rafael", "Raúl", "Ricardo", "Rodrigo", "Rubén", "Salvador", "Sergio", "Tomás", "Vicente"]

NOMBRES = NOMBRES_F + NOMBRES_M

APELLIDOS = ["Aguado", "Alarcón", "Alonso", "Arenas", "Arroyo", "Bermejo", "Blanco", "Bravo", "Caballero", "Calvo", "Campos", "Cano", "Carrasco", "Castaño", "Cortés", "Crespo", "Delgado", "Domínguez", "Durán", "Escobar", "Esteban", "Fajardo", "Ferrer", "Flores", "Fuentes", "Gallego", "Garrido", "Gil", "Giménez", "Guerrero", "Herrera", "Hidalgo", "Iglesias", "Jiménez", "Lara", "Lozano", "Luque", "Manzano", "Marín", "Medina", "Molina", "Montero", "Mora", "Morales", "Navarro", "Nieto", "Núñez", "Ortega", "Ortiz", "Pardo", "Pastor", "Peña", "Prieto", "Quesada", "Ramos", "Reyes", "Rivas", "Robles", "Rojas", "Rubio", "Saez", "Salas", "Sanz", "Serrano", "Soler", "Soto", "Tejada", "Torres", "Valero", "Vargas", "Vega", "Velasco", "Vidal", "Zapata"]

MUNICIPIOS = ["Albacete", "Alcorcón", "Almería", "Ávila", "Badajoz", "Burgos", "Cáceres", "Calatayud", "Cuenca", "Écija", "Ferrol", "Gandía", "Getafe", "Gijón", "Guadalajara", "Huesca", "Jaén", "Jerez", "León", "Linares", "Logroño", "Lorca", "Lugo", "Manresa", "Mérida", "Motril", "Ourense", "Palencia", "Ponferrada", "Reus", "Sagunto", "Salamanca", "Segovia", "Soria", "Talavera", "Teruel", "Toledo", "Úbeda", "Utrera", "Valdepeñas", "Vic", "Vitoria", "Zamora"]

PUEBLOS = ["Albalate", "Alcolea", "Aldeanueva", "Algarra", "Almoguera", "Arcas", "Atienza", "Bañuelos", "Belmonte", "Boniches", "Buenache", "Cañete", "Carrascosa", "Castejón", "Cifuentes", "Cogolludo", "Fuentelencina", "Garcinarro", "Huete", "Jábaga", "Landete", "Mariana", "Mira", "Moya", "Olmedilla", "Palomera", "Pareja", "Priego", "Salvacañete", "Sotos", "Tarancón", "Tragacete", "Uña", "Valdemoro", "Villalba", "Villar", "Yémeda", "Zafra"]

VIAS = ["Almendro", "Acacias", "Álamo", "Cerezo", "Olmo", "Pinar", "Rosal", "Jazmín", "Lirio", "Romero", "Tomillo", "Laurel", "Sauce", "Abedul", "Encina", "Nogal", "Avellano", "Membrillo", "Granado", "Higuera", "Madroño", "Ciprés", "Espino", "Sabina", "Retama", "Brezo", "Junco", "Hiedra", "Malva", "Amapola", "Azucena", "Violeta", "Clavel"]

ACTIVIDADES = ["veterinaria", "farmacéutica", "panadera", "maestra", "cartera", "médica", "herrera", "alcaldesa", "boticaria", "tendera"]


def _partir(lista: list[str]) -> dict[str, list[str]]:
    """Reparte 60 / 20 / 20 de forma determinista (por posición, tras ordenar)."""
    orden = sorted(set(lista))
    trozos: dict[str, list[str]] = {"train": [], "cal": [], "test": []}
    for i, x in enumerate(orden):
        r = i % 5
        trozos["train" if r < 3 else "cal" if r == 3 else "test"].append(x)
    return trozos


PARTICIONES = ("train", "cal", "test")
GAZ = {
    nombre: _partir(lista)
    for nombre, lista in {
        "nombre_f": NOMBRES_F,
        "nombre_m": NOMBRES_M,
        "apellido": APELLIDOS,
        "municipio": MUNICIPIOS,
        "pueblo": PUEBLOS,
        "via": VIAS,
        "actividad": ACTIVIDADES,
    }.items()
}
GAZ["nombre"] = {p: GAZ["nombre_f"][p] + GAZ["nombre_m"][p] for p in PARTICIONES}
