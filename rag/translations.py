# Script para traducir los objetos y componentes al castellano.

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


# Función para traducir la query del usuario en caso de que esté en castellano

def traducir_query(query: str) -> str:
    """
    Reemplaza nombres en español por sus equivalentes en inglés si la query se realiza en español.
    Matchea primero las cadenas más largas para evitar reemplazos parciales si existiera algún caso a futuro.
    """
    # Combinar ambos diccionarios
    traducciones = {**COMPONENTS_ES, **ITEMS_ES}

    # Ordenar por longitud descendente (más largo primero)
    query_lower = query.lower()
    for es, en in sorted(traducciones.items(), key=lambda x: len(x[0]), reverse=True):
        if not es:  # Saltar claves vacías sin rellenar
            continue
        if es.lower() in query_lower:
            query_lower = query_lower.replace(es.lower(), en)

    return query_lower