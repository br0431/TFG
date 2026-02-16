from pathlib import Path
from typing import List, Dict, Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "rag" / "chroma_indexes"

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

COLLECTIONS = {
    "items": {
        "collection_name": "tft_items",
        "persist_dir": CHROMA_DIR / "items",
    },
    "champions": {
        "collection_name": "tft_champions",
        "persist_dir": CHROMA_DIR / "champions",
    },
    "comps": {
        "collection_name": "tft_comps",
        "persist_dir": CHROMA_DIR / "comps",
    },
}
# Carga de un índice ya persistido en chromaDB creado en build_index
def load_vectorstore(index_key: str, embedder: HuggingFaceEmbeddings) -> Chroma:

    cfg = COLLECTIONS[index_key]
    return Chroma(
        collection_name=cfg["collection_name"],
        persist_directory=str(cfg["persist_dir"]),
        embedding_function=embedder,
    )

# Vectoriza la query y devuelve el vector numérico
def embed_query(query: str, embedder: HuggingFaceEmbeddings) -> List[float]:

    return embedder.embed_query(query)

# Búsqueda semántica
def semantic_search( vectorstore: Chroma, query: str, k: int = 3) -> List[Any]:
    """
    Búsqueda semántica:
    - internamente: embebe la query
    - compara con todos los embeddings del índice
    - devuelve los k documentos más similares
    """
    return vectorstore.similarity_search(query, k=k)

def main():
    # Creación del embedder
    embedder = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Elección del índice a consultar
    INDEX_TO_QUERY = "champions"

    # Carga del vectorstore de croma ya persistido
    db = load_vectorstore(INDEX_TO_QUERY, embedder)

    # Querys de ejemplo, una para cada índice
    #query = "Which item is built from Recurve Bow and Needlessly Large Rod?"
    #query = "If I have started the game with Ekko and Blitzcrank which composition is the best"
    query = "Which are the best items for Qiyana"

    # Búsqueda semántica
    results = semantic_search(db, query, k=3)

    print("\n==============================")
    print("MEJORES RESULTADOS")
    print("==============================")

    for i, doc in enumerate(results, start=1):
        print(f"\n=== Result #{i} ===")
        print(doc.page_content)
        print("METADATA:", doc.metadata)

if __name__ == "__main__":
    main()