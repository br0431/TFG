"""
scrapping_items.py - Recopilación de los datos de un objeto desde MetaTFT.
Extrae el nombre, los componentes con los que se construye, las bonificaciones
que otorga y la descripción de su efecto, y guarda el resultado en un fichero
JSON independiente dentro de data/items.
"""
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def scrape_item(url):
    """
    Abre la ficha del objeto indicado y devuelve sus datos ya guardados en disco.
    """

    # Setup del driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    driver.get(url)

    # La ficha carga su contenido de forma dinámica, de modo que la espera
    # previa evita leer la página antes de que los elementos estén disponibles.
    time.sleep(5)

    # NAME
    name = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "ItemDetailHeader"))
    ).text.strip()

    # COMPONENTS
    components = []
    recipe_imgs = driver.find_elements(
        By.CSS_SELECTOR,
        ".ItemDetailRecipeImgs img.RecipeImg"
    )

    # La página no expone el nombre del componente como texto, de manera que se
    # deduce del nombre del fichero de su imagen.
    for img in recipe_imgs:
        src = img.get_attribute("src")
        if not src:
            continue

        filename = src.split("/")[-1]
        raw_name = filename.replace("tft_item_", "").replace(".png", "")
        component_name = raw_name.replace("_", " ").title()

        components.append(component_name)

    # BONUSES
    bonuses = []
    bonus_imgs = driver.find_elements(
        By.CLASS_NAME,
        "ItemDetailBonusImg"
    )

    # El atributo alt llega con el formato "X Bonus:", por lo que se retira ese
    # sufijo para quedarse solo con la bonificación.
    for img in bonus_imgs:
        alt = img.get_attribute("alt")
        if alt:
            bonuses.append(alt.replace(" Bonus:", "").strip())

    # DESCRIPTION
    description = driver.find_element(
        By.CLASS_NAME,
        "ItemDetailDescription"
    ).text.strip()

    driver.quit()

    # ITEM JSON
    item_data = {
        "name": name,
        "components": components,
        "bonuses": bonuses,
        "description": description
    }

    save_item(item_data)
    print(f"✔ Guardado item: {name}")


def save_item(item):
    """
    Guarda el objeto en un fichero JSON nombrado a partir de su denominación.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "items")
    os.makedirs(data_dir, exist_ok=True)

    # El nombre se normaliza a minúsculas y sin caracteres conflictivos para que
    # sirva como nombre de fichero y permita reemplazar un elemento concreto sin
    # regenerar el conjunto.
    safe_name = (
        item["name"]
        .lower()
        .replace(" ", "_")
        .replace("'", "")
    )

    filepath = os.path.join(data_dir, f"{safe_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=4, ensure_ascii=False)


# MAIN
if __name__ == "__main__":
    scrape_item("https://www.metatft.com/items/TFT_Item_Deathblade")