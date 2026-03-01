import json
from pathlib import Path

# Chroma = vector store persistente (almacena embeddings + metadatos).
from langchain_chroma import Chroma
# Document = estructura estándar de LangChain para guardar "texto + metadata".
from langchain_core.documents import Document
# HuggingFaceEmbeddings = wrapper para usar modelos de embeddings de HuggingFace.
from langchain_huggingface import HuggingFaceEmbeddings

# Configuración de variables estáticas para las rutas y el modelo elegido.
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "scrapping" / "data"
CHROMA_DIR = ROOT / "rag" / "chroma_db"

# Modelo de embedding
EMBED_MODEL = "BAAI/bge-base-en-v1.5"


# Proceso de serialización estable para correcta búsqueda semántica
def stable_text_item(obj: dict) -> str:
    """
    En esta función convertimos el JSON a un texto plano consistente sin almacenarlo, simplemente devolviendo la cadena resultante.
    Mantiene siempre el mismo orden de campos, simplemente se eliminan los carácteres que no aportan más que ruido del JSON.
    """
    return "\n".join([
        "TYPE: item",
        f"NAME: {obj.get('name','')}",
        f"COMPONENTS: {', '.join(obj.get('components', []))}",
        f"BONUSES: {', '.join(obj.get('bonuses', []))}",
        f"DESCRIPTION: {obj.get('description','')}",
    ])


def stable_text_champion(obj: dict) -> str:
    """
    En esta función convertimos el JSON a un texto plano consistente sin almacenarlo, simplemente devolviendo la cadena resultante.
    Mantiene siempre el mismo orden de campos, simplemente se eliminan los carácteres que no aportan más que ruido del JSON.
    """
    return "\n".join([
        "TYPE: champion",
        f"NAME: {obj.get('name','')}",
        f"COST: {obj.get('cost','')}",
        f"ROLE: {obj.get('role','')}",
        f"TRAITS: {', '.join(obj.get('traits', []))}",
        f"BEST_ITEMS: {', '.join(obj.get('items', []))}",
        f"UNLOCK: {obj.get('unlock','')}",
    ])


def stable_text_comp(obj: dict) -> str:
    """
    En esta función convertimos el JSON a un texto plano consistente sin almacenarlo, simplemente devolviendo la cadena resultante.
    Mantiene siempre el mismo orden de campos, simplemente se eliminan los carácteres que no aportan más que ruido del JSON.
    Algunas composiciones tienen más de una variante por lo que se va recorriendo la lista de las posibles variantes que tiene la composición.
    """
    lines = ["TYPE: comp", f"NAME: {obj.get('name','')}"]
    for i, v in enumerate(obj.get("variants", []), 1):
        champs = v.get("level_8", {}).get("champions", [])
        add9 = v.get("level_9_addition", "")
        lines.append(f"VARIANT_{i}_LEVEL_8: {', '.join(champs)}")
        if add9:
            lines.append(f"VARIANT_{i}_LEVEL_9_ADDITION: {add9}")
    return "\n".join(lines)


def load_json_files(folder: Path):
    """
    Devuelve todos los ficheros .json de una carpeta.
    Si la carpeta no existe, devuelve una lista vacía.
    """
    if not folder.exists():
        return []
    return list(folder.glob("*.json"))


def main():
    # Garantizamos que existe el directorio del índice en disco.
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # Inicializamos el modelo de embeddings, en este caso BAAI/bge-base-en-v1.5 .
    # normalize_embeddings=True suele mejorar el retrieval con modelos BGE, al no dar fallos lo dejamos así.
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
    # Indexación de los items. El índice contiene el texto estable serializado, el embedding y los metadatos específicados).
    # Lista para guardar los documentos.
    items_docs = []
    # Bucle para leer todos los ficheros .json del directorio y leer el contenido.
    for fp in load_json_files(DATA_DIR / "items"):
        # Conversión de todos los elementos del JSON a diccionario Python.
        obj = json.loads(fp.read_text(encoding="utf-8"))
        # Conversión de cada JSON a un Document con dos partes, texto + metadata.
        items_docs.append(Document(
            page_content=stable_text_item(obj),
            metadata={
                "type": "item",
                "name": obj.get("name", fp.stem),
                "source": str(fp),
                # Guardamos el JSON original como metadata para casos de debug o casos en los que queramos mostrarlo.
                "raw_json": json.dumps(obj, ensure_ascii=False),
            }
        ))
    # Se crea la colección en Chroma en caso de no existir y sino se abre.
    db_items = Chroma(
        collection_name="tft_items",
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )
    if items_docs:
        # Usamos como ID el path del fichero al ser un parámetro estable y evitar duplicados.
        db_items.add_documents(items_docs, ids=[d.metadata["source"] for d in items_docs])

    # Indexación de los campeones. El índice contiene el texto estable serializado, el embedding y los metadatos específicados).
    champs_docs = []
    for fp in load_json_files(DATA_DIR / "champions"):
        obj = json.loads(fp.read_text(encoding="utf-8"))
        champs_docs.append(Document(
            page_content=stable_text_champion(obj),
            metadata={
                "type": "champion",
                "name": obj.get("name", fp.stem),
                "source": str(fp),
                "raw_json": json.dumps(obj, ensure_ascii=False),
            }
        ))

    db_champs = Chroma(
        collection_name="tft_champions",
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )
    if champs_docs:
        db_champs.add_documents(champs_docs, ids=[d.metadata["source"] for d in champs_docs])

    # Indexación de las composiciones. El índice contiene el texto estable serializado, el embedding y los metadatos específicados).
    comps_docs = []
    for fp in load_json_files(DATA_DIR / "comps"):
        obj = json.loads(fp.read_text(encoding="utf-8"))
        comps_docs.append(Document(
            page_content=stable_text_comp(obj),
            metadata={
                "type": "comp",
                "name": obj.get("name", fp.stem),
                "source": str(fp),
                "raw_json": json.dumps(obj, ensure_ascii=False),
            }
        ))

    db_comps = Chroma(
        collection_name="tft_comps",
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )
    if comps_docs:
        db_comps.add_documents(comps_docs, ids=[d.metadata["source"] for d in comps_docs])

    # Comprobación de que se han cargado todos los documentos que tenemos disponibles
    print("JSONs vectorizados con BGE:")
    print(f" - items: {len(items_docs)}")
    print(f" - champions: {len(champs_docs)}")
    print(f" - comps: {len(comps_docs)}")
    print(f"Persistencia en el directorio: {CHROMA_DIR}")


if __name__ == "__main__":
    main()