import json
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "scrapping" / "data"
CHROMA_DIR = BASE_DIR / "rag" / "chroma_indexes"

LIMIT = None
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

def load_json_files(folder: Path, limit=None):
    files = sorted(folder.glob("*.json"))
    if limit:
        files = files[:limit]

    data = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            data.append(json.load(fp))
    return data

def champion_to_text(champ):
    parts = [
        f"{champ['name']} is a cost {champ['cost']} champion in Teamfight Tactics Set 16."
    ]

    if champ.get("role"):
        parts.append(f"Its role is: {', '.join(champ['role'])}.")

    if champ.get("traits"):
        parts.append(f"It has the following traits: {', '.join(champ['traits'])}.")

    if champ.get("items"):
        parts.append(f"Recommended items include: {', '.join(champ['items'])}.")

    if champ.get("unlock"):
        parts.append(f"Special unlock condition: {champ['unlock']}.")

    return " ".join(parts)

def item_to_text(item):
    parts = [
        f"{item['name']} is an item in Teamfight Tactics Set 16."
    ]

    if item.get("components"):
        parts.append(f"It is created by combining: {', '.join(item['components'])}.")

    if item.get("description"):
        parts.append(f"Effect: {item['description']}.")

    return " ".join(parts)


def comp_to_text(comp_name, variant, idx):
    parts = [
        f"{comp_name} composition variant {idx} is a competitive TFT Set 16 composition."
    ]

    lvl8_units = variant["level_8"]["champions"]
    parts.append(
        f"At level 8, the board includes the units: {', '.join(lvl8_units)}."
    )

    if variant.get("level_9_addition"):
        parts.append(
            f"At level 9, an additional unit is added: {variant['level_9_addition']}."
        )

    return " ".join(parts)

def build_index(texts, metadatas, name, persist_path, embedder):
    os.makedirs(persist_path, exist_ok=True)

    db = Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embedder,
        collection_name=name,
        persist_directory=str(persist_path),
    )

    return db

def main():
    embedder = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    champions = load_json_files(DATA_DIR / "champions", LIMIT)
    champ_texts = [champion_to_text(c) for c in champions]
    champ_meta = [{"type": "champion", "name": c["name"]} for c in champions]

    build_index(
        champ_texts,
        champ_meta,
        "tft_champions",
        CHROMA_DIR / "champions",
        embedder
    )

    items = load_json_files(DATA_DIR / "items", LIMIT)
    item_texts = [item_to_text(i) for i in items]
    item_meta = [{"type": "item", "name": i["name"]} for i in items]

    build_index(
        item_texts,
        item_meta,
        "tft_items",
        CHROMA_DIR / "items",
        embedder
    )

    comps = load_json_files(DATA_DIR / "comps", LIMIT)

    comp_texts = []
    comp_meta = []

    for comp in comps:
        for idx, variant in enumerate(comp["variants"], start=1):
            comp_texts.append(
                comp_to_text(comp["name"], variant, idx)
            )
            comp_meta.append({
                "type": "composition",
                "name": comp["name"],
                "variant": idx
            })

    build_index(
        comp_texts,
        comp_meta,
        "tft_comps",
        CHROMA_DIR / "comps",
        embedder
    )
    print("Índices de ChromaDb creados correctamente.")

if __name__ == "__main__":
    main()
