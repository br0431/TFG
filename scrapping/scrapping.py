import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def scrape_champion(url: str):

    # Setup del driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 15)

    driver.get(url)

    # NAME (limpio)
    name = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "UnitNameHeader"))
    ).text.strip().splitlines()[0]

    # TRAITS
    trait_elements = driver.find_elements(By.CLASS_NAME, "NewSetUnitTrait")
    traits = [t.text.strip() for t in trait_elements if t.text.strip()]

    # COST
    cost = int(
        driver.find_element(By.CLASS_NAME, "NewSetUnitCost").text.strip()
    )

    # UNLOCK (si existe)
    unlock = ""
    unlock_blocks = driver.find_elements(
        By.CLASS_NAME, "UnitUnlockDescriptionCondition"
    )
    if unlock_blocks:
        parts = []
        for block in unlock_blocks:
            text = block.text.replace("\n", " ").strip()
            if text:
                parts.append(text)
        unlock = " | ".join(parts)

    # ITEMS (Recommended Builds)
    items = []

    try:
        build_container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ItemDetailHolders .UnitBuildContainer")
            )
        )

        item_imgs = build_container.find_elements(
            By.CSS_SELECTOR, "img.TableItemImg"
        )

        for img in item_imgs[:3]:
            alt = img.get_attribute("alt")
            if alt:
                items.append(alt)

    except Exception as e:
        print("⚠️ No se han podido scrappear los items:", e)
        items = []

    driver.quit()

    # Champion final
    champion = {
        "name": name,
        "cost": cost,
        "traits": traits,
        "items": items,
        "unlock": unlock
    }

    save_champion(champion)
    print(f"✔ Guardado: {name}")


def save_champion(champion: dict):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "champions")
    os.makedirs(data_dir, exist_ok=True)

    safe_name = (
        champion["name"]
        .lower()
        .strip()
        .replace("\n", "")
        .replace(" ", "_")
        .replace("'", "")
        .replace(".", "")
    )

    filepath = os.path.join(data_dir, f"{safe_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(champion, f, indent=4, ensure_ascii=False)

# EJECUCIÓN
if __name__ == "__main__":
    scrape_champion("https://www.metatft.com/units/Neeko")
