"""
scrapping_comps.py - Recopilación de las composiciones de mayor rendimiento desde MetaTFT.
Recorre el listado de composiciones de la fuente y guarda, para cada una, las unidades
que la integran a nivel ocho y la unidad que conviene incorporar al alcanzar el nivel
nueve, en un fichero JSON independiente dentro de data/comps.
"""
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Listado de composiciones ordenadas por rendimiento del que parte la recopilación.
COMPS_URL = "https://www.metatft.com/comps"

# La fuente no publica la unidad que conviene añadir al subir al nivel nueve, de modo
# que esa correspondencia se ha establecido a partir del criterio del autor como jugador
# y se consulta durante la extracción.
LEVEL_9_ADDITIONS = {
    "Bilgewater Miss Fortune": "Fiddlesticks",
    "Zaun Warwick": "Ziggs",
    "Zaun Ekko": "Fiddlesticks",
    "Yordle Veigar": "Swain",
    "Warden Kalista": "Fiddlesticks",
    "Ionia Yunara": "Shyvana",
    "Demacia Lux": "Ziggs",
    "Demacia Kaisa": "Ziggs"
}


def scrape_comps(limit=10):
    """
    Recorre el listado de composiciones y guarda en disco las primeras que encuentre.
    El parámetro limit acota el número de composiciones recopiladas.
    """
    # Setup del driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(COMPS_URL)

    # La espera permite aceptar el aviso de cookies y ajustar la vista del navegador,
    # ya que la disposición predeterminada no muestra de forma simultánea todos los
    # elementos que deben recuperarse.
    print("Esperando 15 segundos para aceptar cookies y ajustar vista (necesario scrapping)...")
    time.sleep(15)

    # Cada fila del listado contiene una composición completa con sus unidades.
    comp_rows = driver.find_elements(By.CLASS_NAME, "CompRowWrapper")

    scraped = 0
    for comp in comp_rows:
        if scraped >= limit:
            break

        result = scrape_single_comp(comp)
        if not result:
            continue

        save_comp(result)
        scraped += 1
        print(f"Guardada la comp {scraped}: {result['name']}")

    driver.quit()


def scrape_single_comp(comp):
    """
    Extrae de una fila del listado el nombre de la composición y sus unidades.
    Devuelve None cuando la fila no corresponde a una composición válida.
    """
    try:
        full_name = comp.find_element(By.CLASS_NAME, "CompRowName").text.strip()
    # Las filas sin nombre corresponden a elementos de la página ajenos al listado
    # de composiciones, por lo que se descartan.
    except:
        return None

    if not full_name:
        return None

    # La fuente antepone al nombre la sinergia principal de la composición.
    synergy = full_name.split()[0]

    champions = []
    unit_links = comp.find_elements(
        By.CSS_SELECTOR, ".Unit_Wrapper a[href*='/units/']"
    )

    # El nombre de cada unidad se deduce del enlace que apunta a su ficha, ya que
    # la fila no lo expone como texto.
    for link in unit_links:
        href = link.get_attribute("href")
        if href:
            champ = href.split("/units/")[-1]
            champ = champ.replace("-", " ").title()
            champions.append(champ)

    if not champions:
        return None

    # La composición se identifica por su sinergia principal y por la primera unidad
    # del listado, que es la que vertebra la formación.
    comp_name = f"{synergy} {champions[0]}"
    level_9_addition = LEVEL_9_ADDITIONS.get(comp_name, "")

    return {
        "name": comp_name,
        "level_8": {
            "champions": champions
        },
        "level_9_addition": level_9_addition
    }


def save_comp(comp):
    """
    Guarda la composición en un fichero JSON nombrado a partir de su denominación.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "comps")
    os.makedirs(data_dir, exist_ok=True)

    safe_name = comp["name"].lower().replace(" ", "_").replace("'", "")
    filepath = os.path.join(data_dir, f"{safe_name}.json")

    new_variant = {
        "level_8": comp["level_8"],
        "level_9_addition": comp["level_9_addition"]
    }

    # Una misma composición admite varias variantes, de manera que si el fichero ya
    # existe la nueva se añade a las registradas en lugar de sobrescribirlo.
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["variants"].append(new_variant)

    else:
        data = {
            "name": comp["name"],
            "variants": [new_variant]
        }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# MAIN
if __name__ == "__main__":
    scrape_comps(limit=10)