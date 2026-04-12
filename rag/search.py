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

def classify_query(query: str) -> list[str]:
    """
    Clasifica la intención de la query usando keywords.
    Devuelve una lista con las colecciones relevantes: item, champion, comp.
    """
    q = query.lower()

    item_keywords     = {"item", "items", "component", "components", "bonus", "bonuses", "equip", "build", "bis", "best in slot"}
    champion_keywords = {"item", "items", "champion", "champions", "who", "cost", "trait", "traits", "ability", "stats"}
    comp_keywords     = {"comp", "composition", "compositions", "team", "synergy", "synergies", "play", "lineup", "board"}

    detected = []
    if any(k in q for k in item_keywords):
        detected.append("item")
    if any(k in q for k in champion_keywords):
        detected.append("champion")
    if any(k in q for k in comp_keywords):
        detected.append("comp")

    # "best items for [champion]" la info está en la colección champion, no en item.
    if "item" in detected and "champion" in detected:
        detected.remove("item")
    # Devolvemos las colecciones encontradas y en caso de no haber encontrado ninguna, devolvemos todas.
    return detected if detected else ["item", "champion", "comp"]


def main():
    # Inicializamos el modelo de embeddings.
    # normalize_embeddings=True normaliza los vectores y suele estabilizar las similitudes.
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    # Cargamos las colecciones ya indexadas en Chroma separando por colecciones para mejorar la búsqueda.
    db_items = Chroma("tft_items", persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    db_champs = Chroma("tft_champions", persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    db_comps = Chroma("tft_comps", persist_directory=str(CHROMA_DIR), embedding_function=embeddings)

    # Mapeamos cada colección a su db para simplificar el enrutado.
    collection_map = {
        "item": db_items,
        "champion": db_champs,
        "comp": db_comps,
    }

    # Inicializamos el modelo LLM en local a través de Ollama.
    # temperature=0 para respuestas más deterministas (útil en pruebas y evaluación). Contexto en la incialización reducido para evitar problemas de saturación de GPU
    llm = OllamaLLM(model=LLM_MODEL, temperature=0, num_ctx=2048)

    print("Escribe tu pregunta sobre el set 16 del TFT. ENTER vacío para salir.")

    while True:
        # Lectura de la query del usuario en consola.
        query = input("\n> ").strip()

        # Salimos si el usuario no escribe nada.
        if not query:
            break

        # Clasificación automática: puede devolver una o varias colecciones.
        collections = classify_query(query)
        print(f"[Colecciones detectadas: {', '.join(collections)}]")

        # Buscamos en todas las colecciones identificadas y fusionamos los docs. Se divide el máximo de k documentos devueltos entre el número de colecciones buscadas para repartir los resultados. Se usa max por si pusieramos k=1 y buscara en 3 colecciones que no fuera 0.
        k_per_col = max(1, MAX_DOCS // len(collections))
        docs = []
        for col in collections:
            docs.extend(collection_map[col].similarity_search("query: " + query, k=k_per_col))

        # Debug para ver que resultados se devuelven antes de validar la respuesta del LLM.
        print("\n[Recuperados]")
        for i, d in enumerate(docs, 1):
            print(f"{i}. {d.metadata.get('type')} | {d.metadata.get('name')}")

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
            "You are a TFT expert. The user asked a multi-part question. "
            "Answer EVERY part using ONLY the documents below but do not mention them in the answer.\n"
            "Go through each document and use it if it is relevant to any part of the question.\n"
            "If a part of the answer is not in the documents, say: I don't have that information.\n\n"
            f"Question: {query}\n\n"
            f"Documents:\n{context}\n\n"
            "Answer:"
        )
        # Invocamos el LLM con el prompt completo.
        # El modelo generará la respuesta basándose únicamente en la evidencia del contexto.
        print("\nRespuesta generada por el LLM:\n", llm.invoke(prompt))


if __name__ == "__main__":
    main()
