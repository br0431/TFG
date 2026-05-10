from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

# Configuración de variables estáticas para las rutas y el modelo elegido.
ROOT       = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT / "rag" / "chroma_db"
# Modelo de embedding.
EMBED_MODEL = "BAAI/bge-base-en-v1.5"
# Modelo del LLM ejecutado en local con Ollama instalado.
LLM_MODEL = "llama3.1:8b"
# Número máximo de documentos recuperados tras la búsqueda semántica.
MAX_DOCS = 4
# Máximo de caractéres por documento para no tener problemas de memoria.
MAX_CHARS_PER_DOC = 450
# Estado global del RAG. Se inicializa una sola vez en la primera llamada a ask()
# para evitar cargar los modelos y las colecciones en cada petición HTTP.
_rag = None


def classify_query(query: str) -> list[str]:
    """
    Clasifica la intención de la query usando keywords.
    Devuelve una lista con las colecciones relevantes: item, champion, comp.
    """
    q = query.lower()

    item_keywords     = {"item", "items", "component", "components", "bonus", "bonuses", "equip", "build", "bis", "best in slot"}
    champion_keywords = {"item", "items", "champion", "champions", "who", "cost", "trait", "traits", "ability", "stats"}
    comp_keywords     = {"comp", "composition", "compositions", "team", "synergy", "synergies", "play", "lineup", "board"}
    recipe_keywords   = {"component", "components", "built from", "made from", "craft", "combine", "recipe"}

    detected = []
    if any(k in q for k in item_keywords):
        detected.append("item")
    if any(k in q for k in champion_keywords):
        detected.append("champion")
    if any(k in q for k in comp_keywords):
        detected.append("comp")

    # Si la query mezcla items y campeones, decidimos la colección por contexto.
    if "item" in detected and "champion" in detected:
        if any(k in q for k in recipe_keywords):
            detected.remove("champion")
        else:
            detected.remove("item")

    return detected if detected else ["item", "champion", "comp"]


def _init_rag():
    """
    Inicializa embeddings, colecciones Chroma y LLM.
    Si ya se habían inicializado previamente, devuelve la instancia existente.
    """
    global _rag
    if _rag is not None:
        return _rag

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    db_items  = Chroma("tft_items",     persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    db_champs = Chroma("tft_champions", persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    db_comps  = Chroma("tft_comps",     persist_directory=str(CHROMA_DIR), embedding_function=embeddings)

    llm = OllamaLLM(model=LLM_MODEL, temperature=0, num_ctx=2048)

    _rag = {
        "collection_map": {"item": db_items, "champion": db_champs, "comp": db_comps},
        "llm": llm,
    }
    return _rag

def ask(query: str) -> str:
    """
    Punto de entrada para el chat libre. Recibe la query completa
    (incluyendo el contexto del tablero si lo hay) y devuelve la respuesta
    del LLM como string, lista para mostrar en el chat.
    """
    rag = _init_rag()
    collection_map = rag["collection_map"]
    llm = rag["llm"]

    collections = classify_query(query)

    k_per_col = max(1, MAX_DOCS // len(collections))
    docs = []
    for col in collections:
        docs.extend(collection_map[col].similarity_search("query: " + query, k=k_per_col))

    docs_block = []
    for i, d in enumerate(docs, 1):
        content = d.page_content[:MAX_CHARS_PER_DOC]
        docs_block.append(
            f"[D{i}] type={d.metadata.get('type')} name={d.metadata.get('name')}\n"
            f"{content}"
        )

    context = "\n\n---\n\n".join(docs_block)

    prompt = (
        "You are a TFT Set 16 expert assistant. "
        "Answer the user's question using ONLY the information in the documents below. "
        "Go through each document and use it if it is relevant to the question. "
        "Do not mention the documents in your answer. "
        "If the information is not in any document, say so briefly.\n\n"
        f"Question: {query}\n\n"
        f"Documents:\n{context}\n\n"
        "Answer:"
    )

    return llm.invoke(prompt)


def ask_advice(prompt: str, champions: list[str]) -> str:
    """
    Punto de entrada específico para el motor de decisiones.
    Busca composiciones y detalles de campeones via vector search,
    usando los nombres de campeones como query para mayor precisión.
    """
    rag = _init_rag()
    collection_map = rag["collection_map"]
    llm = rag["llm"]

    # La query de búsqueda son solo los nombres de campeones, no el prompt completo.
    # Así el vector search compara directamente contra los nombres en los documentos.
    search_query = "champions: " + ", ".join(champions) if champions else prompt

    k_per_col = max(1, MAX_DOCS // 2)
    comp_docs  = collection_map["comp"].similarity_search("query: " + search_query, k=k_per_col)
    champ_docs = collection_map["champion"].similarity_search("query: " + search_query, k=k_per_col)

    comp_block = []
    for i, d in enumerate(comp_docs, 1):
        comp_block.append(f"[COMP{i}] {d.page_content[:MAX_CHARS_PER_DOC]}")

    champ_block = []
    for i, d in enumerate(champ_docs, 1):
        champ_block.append(f"[CHAMP{i}] {d.page_content[:MAX_CHARS_PER_DOC]}")

    comp_context  = "\n\n".join(comp_block)
    champ_context = "\n\n".join(champ_block)

    system_prompt = (
        "You are a TFT Set 16 expert coach.\n"
        "The player has shared their current game state.\n"
        "Do not reference document labels like [COMP1] or [CHAMP1] in your answer.\n"
        f"Player situation:\n{prompt}\n\n"
        f"Available compositions:\n{comp_context}\n\n"
        f"Champion details:\n{champ_context}\n\n"
        "Instructions:\n"
        "1. Recommend the composition that best matches the player's current champions.\n"
        "2. List the units they still need to find to complete it.\n"
        "3. Tell them which of their current units are NOT in this comp and can be sold.\n"
        "4. If they have items, say which champion should hold them.\n"
        "5. If no composition matches their current units, say so honestly.\n"
        "Be specific and concise.\n\n"
        "Recommendation:"
    )

    return llm.invoke(system_prompt)


def main():
    print("Escribe tu pregunta sobre el set 16 del TFT. ENTER vacío para salir.")
    while True:
        query = input("\n> ").strip()
        if not query:
            break
        collections = classify_query(query)
        print(f"[Colecciones detectadas: {', '.join(collections)}]")
        print("\nRespuesta generada por el LLM:\n", ask(query))


if __name__ == "__main__":
    main()