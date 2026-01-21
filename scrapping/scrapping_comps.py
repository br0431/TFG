import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


COMPS_URL = "https://www.metatft.com/comps"

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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(COMPS_URL)

    print("Esperando 15 segundos para aceptar cookies y ajustar vista (necesario scrapping)...")
    time.sleep(15)

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
    try:
        full_name = comp.find_element(By.CLASS_NAME, "CompRowName").text.strip()
    except:
        return None

    if not full_name:
        return None

    synergy = full_name.split()[0]

    champions = []
    unit_links = comp.find_elements(
        By.CSS_SELECTOR, ".Unit_Wrapper a[href*='/units/']"
    )

    for link in unit_links:
        href = link.get_attribute("href")
        if href:
            champ = href.split("/units/")[-1]
            champ = champ.replace("-", " ").title()
            champions.append(champ)

    if not champions:
        return None

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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "comps")
    os.makedirs(data_dir, exist_ok=True)

    safe_name = comp["name"].lower().replace(" ", "_").replace("'", "")
    filepath = os.path.join(data_dir, f"{safe_name}.json")

    new_variant = {
        "level_8": comp["level_8"],
        "level_9_addition": comp["level_9_addition"]
    }

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


if __name__ == "__main__":
    scrape_comps(limit=10)


