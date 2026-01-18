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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)

    driver.get(url)

    time.sleep(5)

    name = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "ItemDetailHeader"))
    ).text.strip()

    components = []
    recipe_imgs = driver.find_elements(
        By.CSS_SELECTOR,
        ".ItemDetailRecipeImgs img.RecipeImg"
    )

    for img in recipe_imgs:
        src = img.get_attribute("src")
        if not src:
            continue

        filename = src.split("/")[-1]
        raw_name = filename.replace("tft_item_", "").replace(".png", "")
        component_name = raw_name.replace("_", " ").title()

        components.append(component_name)

    bonuses = []
    bonus_imgs = driver.find_elements(
        By.CLASS_NAME,
        "ItemDetailBonusImg"
    )

    for img in bonus_imgs:
        alt = img.get_attribute("alt")
        if alt:
            bonuses.append(alt.replace(" Bonus:", "").strip())

    description = driver.find_element(
        By.CLASS_NAME,
        "ItemDetailDescription"
    ).text.strip()

    driver.quit()

    item_data = {
        "name": name,
        "components": components,
        "bonuses": bonuses,
        "description": description
    }

    save_item(item_data)
    print(f"✔ Guardado item: {name}")


def save_item(item):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "items")
    os.makedirs(data_dir, exist_ok=True)

    safe_name = (
        item["name"]
        .lower()
        .replace(" ", "_")
        .replace("'", "")
    )

    filepath = os.path.join(data_dir, f"{safe_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    scrape_item("https://www.metatft.com/items/TFT_Item_Deathblade")
