"""
translations.py - Traducción de la terminología del videojuego del castellano al inglés.
La base de conocimiento se almacena íntegramente en inglés, de modo que las consultas
formuladas en castellano se reescriben antes de la clasificación y de la búsqueda
semántica para que los nombres y los términos coincidan con el contenido indexado.
"""

# Los ocho componentes básicos, cuyos nombres en inglés se escriben sin espacios
# por ser así como aparecen en la fuente de datos.
COMPONENTS_ES = {
    "Espadón":                          "Bfsword",
    "Chaleco de Cadenas":               "Chainvest",
    "Cinturón de Gigante":              "Giantsbelt",
    "Vara Innecesariamente Grande":     "Needlesslylargerod",
    "Capa Negatrón":                    "Negatroncloak",
    "Arco Curvo":                       "Recurvebow",
    "Guantes de Combate":               "Sparringgloves",
    "Lágrima de la Diosa":              "Tearofthegoddess",
}

# Los objetos completos, traducidos a partir de la denominación oficial que el
# videojuego emplea en su versión en castellano.
ITEMS_ES = {
    "Yelmo Adaptable":                  "Adaptive Helm",
    "Bastón del Arcángel":              "Archangels Staff",
    "Sanguinaria":                      "Bloodthirster",
    "Mejora Azul":                      "Blue Buff",
    "Chaleco de Zarzas":                "Bramble Vest",
    "Regiaguardia":                     "Crownguard",
    "Filo Mortal":                      "Deathblade",
    "Garra de Dragón":                  "Dragon's Claw",
    "Filo de la Noche":                 "Edge of Night",
    "Mortaja de la Quietud":            "Evenshroud",
    "Protector Pétreo de Gárgola":      "Gargoyle Stoneplate",
    "Verdugo de Gigantes":              "Giant Slayer",
    "Hoja de la Furia de Guinsoo":      "Guinsoo's Rageblade",
    "Mano de la Justicia":              "Hand Of Justice",
    "Sable-Pistola Hextech":            "Hextech Gunblade",
    "Filo Infinito":                    "Infinity Edge",
    "Chispa Iónica":                    "Ionic Spark",
    "Guantelete Enjoyado":              "Jeweled Gauntlet",
    "Furia del Kraken":                 "Kraken's Fury",
    "Últimas Palabras":                 "Last Whisper",
    "Morellonomicon":                   "Morellonomicon",
    "Diente de Nashor":                 "Nashor's Tooth",
    "Promesa del Protector":            "Protector's Vow",
    "Fajín de Mercurio":                "Quicksilver",
    "Sombrero Mortal de Rabadon":       "Rabadon's Deathcap",
    "Mejora Roja":                      "Red Buff",
    "Lanza de Shojin":                  "Spear of Shojin",
    "Rostro Espiritual":                "Spirit Visage",
    "Corazón Resuelto":                 "Steadfast Heart",
    "Calibrador de Sterak":             "Sterak's Gage",
    "Mangual del Guerrero":             "Striker's Flail",
    "Capa de Fuego Solar":              "Sunfire Cape",
    "Guantes de Ladrón":                "Thief's Gloves",
    "Resolución Titánica":              "Titan's Resolve",
    "Bastón del Vacío":                 "Void Staff",
    "Armadura de Warmog":               "Warmog's Armor",
}

# Terminología general de TFT para que classify_query y ChromaDB trabajen correctamente cuando el usuario escribe en castellano y no falle.
TERMS_ES = {
    "objetos":                          "items",
    "objeto":                           "item",
    "campeones":                        "champions",
    "campeón":                          "champion",
    "composiciones":                    "compositions",
    "composición":                      "composition",
    "componentes":                      "components",
    "componente":                       "component",
    "sinergias":                        "traits",
    "sinergia":                         "trait",
    "equipo":                           "team",
    "equipar":                          "equip",
    "rasgos":                           "traits",
    "rasgo":                            "trait",
    "habilidad":                        "ability",
    "coste":                            "cost",
    "jugar":                            "play",
    "tablero":                          "board",
    "mesa":                             "board",
    "receta":                           "recipe",
    "combinar":                         "combine",
    "bonificación":                     "bonus",
    "bonificaciones":                   "bonuses",
    "quién":                            "who",
    "estadísticas":                     "stats",
    "alineación":                       "lineup",
    "fabricar":                         "craft",
    "se hace con":                      "made from",
    "se fabrica con":                   "built from",
    "se construye con":                 "built from",
    "construye":                        "build"
}


# Función para traducir la query del usuario en caso de que esté en castellano

def traducir_query(query: str) -> str:
    """
    Reemplaza nombres en español por sus equivalentes en inglés si la query se realiza en español.
    Compara primero las cadenas más largas para evitar reemplazos parciales.
    """

    # Combinar los tres diccionarios
    traducciones = {**COMPONENTS_ES, **ITEMS_ES, **TERMS_ES}

    # Se retiran los signos de apertura propios del castellano, que no aparecen en
    # los documentos indexados.
    query_lower = query.lower().replace("¿", "").replace("¡", "")
    # El recorrido va de la cadena más larga a la más corta para que una expresión
    # compuesta se sustituya antes que cualquiera de sus palabras por separado.
    for es, en in sorted(traducciones.items(), key=lambda x: len(x[0]), reverse=True):
        if not es:
            continue
        if es.lower() in query_lower:
            query_lower = query_lower.replace(es.lower(), en)

    return query_lower