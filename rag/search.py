from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings

# Configuración de variables estáticas para las rutas y el modelo elegido.
ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT / "rag" / "chroma_db"
# Modelo de embedding.
EMBED_MODEL = "BAAI/bge-base-en-v1.5"
# Modelo del LLM ejecutado en local con Ollama instalado.
LLM_MODEL = "llama3.1:8b"
# Número máximo de documentos recuperados tras la búsqueda semántica.
MAX_DOCS = 4
# Máximo de caractéres por documento para no tener problemas de memoria.
MAX_CHARS_PER_DOC = 450
# # Estado global del RAG. Se inicializa una sola vez en la primera llamada a ask() para evitar cargar los modelos y las colecciones en cada petición HTTP.
_rag= None


def classify_query(query: str) -> list[str]:
    """
    Clasifica la intención de la query usando keywords.
    Devuelve una lista con las colecciones relevantes: item, champion, comp.
    """
    q = query.lower()

    item_keywords     = {"item", "items", "component", "components", "bonus", "bonuses", "equip", "build", "bis", "best in slot"}
    champion_keywords = {"item", "items", "champion", "champions", "who", "cost", "trait", "traits", "ability", "stats"}
    comp_keywords     = {"comp", "composition", "compositions", "team", "synergy", "synergies", "play", "lineup", "board"}
    # Palabras que indican una query de crafteo/receta: la info está en tft_items, no en tft_champions.
    recipe_keywords   = {"component", "components", "built from", "made from", "craft", "combine", "recipe"}

    detected = []
    if any(k in q for k in item_keywords):
        detected.append("item")
    if any(k in q for k in champion_keywords):
        detected.append("champion")
    if any(k in q for k in comp_keywords):
        detected.append("comp")

    # Si la query mezcla items y campeones, decidimos la colección por contexto:
    # - query de crafteo entonces tft_items tiene la info de componentes.
    # - query de recomendación entonces tft_champions tiene los mejores items por campeón.
    if "item" in detected and "champion" in detected:
        if any(k in q for k in recipe_keywords):
            detected.remove("champion")
        else:
            detected.remove("item")

    return detected if detected else ["item", "champion", "comp"]
# main simplificado que usa la función ask.
def main():
    print("Escribe tu pregunta sobre el set 16 del TFT. ENTER vacío para salir.")
    while True:
        query = input("\n> ").strip()
        if not query:
            break
        collections = classify_query(query)
        print(f"[Colecciones detectadas: {', '.join(collections)}]")
        print("\nRespuesta generada por el LLM:\n", ask(query))

def _init_rag():
    """
    Inicializa embeddings, colecciones Chroma y LLM.
    Si ya se habían inicializado previamente, devuelve la instancia existente.
    """
    global _rag
    if _rag is not None:
        return _rag

    # Cargamos el modelo de embeddings.
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    # Conectamos con las tres colecciones ya indexadas en Chroma.
    db_items  = Chroma("tft_items",     persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    db_champs = Chroma("tft_champions", persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    db_comps  = Chroma("tft_comps",     persist_directory=str(CHROMA_DIR), embedding_function=embeddings)

    # Inicializamos el LLM.
    llm = OllamaLLM(model=LLM_MODEL, temperature=0, num_ctx=2048)
    # Asignamos a la variable que se va a devolver el contenido, en este caso las colecciones y el llm.
    _rag = {
        "collection_map": {"item": db_items, "champion": db_champs, "comp": db_comps},
        "llm": llm,
    }
    return _rag


def ask(query: str) -> str:
    """
    Punto de entrada para la interfaz web. Recibe la query completa
    (incluyendo el contexto del tablero si lo hay) y devuelve la respuesta
    del LLM como string, lista para mostrar en el chat.
    """
    # Inicializamos el RAG y asignamos valores a las variables a tratar.
    rag = _init_rag()
    collection_map = rag["collection_map"]
    llm = rag["llm"]

    # Clasificación automática de las colecciones a tratar, puede devolver una o varias colecciones.
    collections = classify_query(query)

    # Buscamos en todas las colecciones identificadas y fusionamos los documentos. Se divide el máximo de k documentos entre el número de colecciones buscadas.
    k_per_col = max(1, MAX_DOCS // len(collections))
    docs = []
    for col in collections:
        docs.extend(collection_map[col].similarity_search("query: " + query, k=k_per_col))

    # Construimos un contexto enumerado (D1, D2, D3...) para que el LLM pueda referenciar cada documento recuperado.
    docs_block = []
    for i, d in enumerate(docs, 1):
        content = d.page_content[:MAX_CHARS_PER_DOC]
        docs_block.append(
            f"[D{i}] type={d.metadata.get('type')} name={d.metadata.get('name')}\n"
            f"{content}"
        )

    # Unimos los documentos con separadores claros.
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

    # Invocamos el LLM y devolvemos la respuesta como string.
    return llm.invoke(prompt)

if __name__ == "__main__":
    main()
