import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "scrapping", "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "rag", "documents")

# For testing use 3, for full run use None
LIMIT = 3

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def load_json_files(folder, limit=None):
    files = sorted([f for f in os.listdir(folder) if f.endswith(".json")])
    if limit:
        files = files[:limit]

    data = []
    for file in files:
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            data.append(json.load(f))

    return data


def safe_filename(name):
    return name.lower().replace(" ", "_").replace("'", "")


def champion_to_text(champion):
    lines = []

    lines.append(
        f"{champion['name']} is a cost {champion['cost']} champion in Teamfight Tactics Set 16."
    )

    if champion.get("traits"):
        lines.append(
            f"Its traits are: {', '.join(champion['traits'])}."
        )

    if champion.get("items"):
        lines.append(
            f"Recommended items for this champion include: {', '.join(champion['items'])}."
        )

    if champion.get("unlock"):
        lines.append(
            f"Special unlock condition: {champion['unlock']}."
        )

    return "\n".join(lines)


def item_to_text(item):
    lines = []

    lines.append(
        f"{item['name']} is an item in Teamfight Tactics Set 16."
    )

    if item.get("components"):
        lines.append(
            f"It is built from the following components: {', '.join(item['components'])}."
        )

    if item.get("bonuses"):
        lines.append(
            f"It provides the following stats: {', '.join(item['bonuses'])}."
        )

    if item.get("description"):
        lines.append(
            f"Item effect: {item['description']}."
        )

    return "\n".join(lines)


def comp_variant_to_text(comp_name, variant, index):
    lines = []

    lines.append(
        f"{comp_name} (variant {index}) is a competitive composition in Teamfight Tactics Set 16."
    )

    level_8_units = variant["level_8"]["champions"]
    lines.append(
        f"At level 8, the composition includes the following champions: {', '.join(level_8_units)}."
    )

    if variant.get("level_9_addition"):
        lines.append(
            f"At level 9, an additional unit is commonly added: {variant['level_9_addition']}."
        )

    return "\n".join(lines)


def generate_documents(entity):
    input_dir = os.path.join(DATA_DIR, entity)
    output_dir = os.path.join(OUTPUT_DIR, entity)

    ensure_dir(output_dir)

    entries = load_json_files(input_dir, LIMIT)

    for entry in entries:
        if entity == "champions":
            text = champion_to_text(entry)
            name = entry["name"]
            filename = safe_filename(name)
            filepath = os.path.join(output_dir, f"{filename}.txt")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"📄 Champion document created: {filepath}")

        elif entity == "items":
            text = item_to_text(entry)
            name = entry["name"]
            filename = safe_filename(name)
            filepath = os.path.join(output_dir, f"{filename}.txt")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"📄 Item document created: {filepath}")

        elif entity == "comps":
            comp_name = entry["name"]
            base_filename = safe_filename(comp_name)

            for idx, variant in enumerate(entry["variants"], start=1):
                text = comp_variant_to_text(comp_name, variant, idx)
                filepath = os.path.join(
                    output_dir,
                    f"{base_filename}_variant_{idx}.txt"
                )

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"📄 Composition document created: {filepath}")


if __name__ == "__main__":
    generate_documents("champions")
    generate_documents("items")
    generate_documents("comps")
