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
# Número de documentos recuperados tras la búsqueda semántica.
TOP_K = 3


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

    # Inicializamos el modelo LLM en local a través de Ollama.
    # temperature=0 para respuestas más deterministas (útil en pruebas y evaluación).
    llm = OllamaLLM(model=LLM_MODEL, temperature=0)

    # Información para el usuario sobre el uso de las querys.
    print("Prefijo para elegir colección en la que buscar:")
    print("  item: query | champion: query | comp: query")
    print("ENTER vacío para salir o CTRL C para parar la consola.")

    while True:
        # Lectura de la query del usuario en consola.
        raw = input("\n> ").strip()

        # Salimos si el usuario no escribe nada.
        if not raw:
            break

        # Enrutado manual según el prefijo.
        # item: busca en la colección de items
        if raw.lower().startswith("item:"):
            # Separamos la query y nos quedamos con la consulta del usuario sin el prefijo ya que hemos filtrado previamente.
            query = raw.split(":", 1)[1].strip()
            # similarity_search realiza búsqueda semántica y devuelve los TOP_K documentos más similares.
            # Se añade "query: " como etiqueta de la consulta (heurística para reforzar el rol de query).
            docs = db_items.similarity_search("query: " + query, k=TOP_K)

        # champion: busca en la colección de campeones.
        elif raw.lower().startswith("champion:"):
            query = raw.split(":", 1)[1].strip()
            docs = db_champs.similarity_search("query: " + query, k=TOP_K)

        # comp: busca en la colección de composiciones.
        elif raw.lower().startswith("comp:"):
            query = raw.split(":", 1)[1].strip()
            docs = db_comps.similarity_search("query: " + query, k=TOP_K)
        else:
            # Si el usuario hace la query con un formato inválido se devuelve el formato esperado.
            print("Formato: item: query | champion: query | comp: query")
            continue

        # Debug para ver que resultados se devuelven antes de validar la respuesta del LLM.
        print("\n[Recuperados]")
        for i, d in enumerate(docs, 1):
            print(f"{i}. {d.metadata.get('type')} | {d.metadata.get('name')}")

        # ------------------------------------------------------------
        # AÑADIDO: Enumeración de documentos + instrucción para que el LLM
        # "evalúe" cuáles son los más relevantes y cite cuáles usa.
        # ------------------------------------------------------------

        # Construimos un contexto enumerado (D1, D2, D3...) para que el LLM pueda referenciar cada doc.
        docs_block = []
        for i, d in enumerate(docs, 1):
            docs_block.append(
                f"[D{i}] type={d.metadata.get('type')} name={d.metadata.get('name')}\n"
                f"{d.page_content}"
            )

        # Unimos los documentos con separadores claros.
        context = "\n\n---\n\n".join(docs_block)

        # Prompt modificado:
        # 1) obliga al modelo a decidir qué documento(s) son más relevantes
        # 2) obliga a responder SOLO con esos documentos
        # 3) obliga a citar las fuentes en formato "Sources: [D1, D3]"
        prompt = (
            "You are an expert Teamfight Tactics assistant.\n"
            "You must answer using ONLY the information in the documents below.\n"
            "Task:\n"
            f"1) Decide which document(s) [D1..D{len(docs)}] are most relevant to the question.\n"
            "2) Answer the question using ONLY those documents.\n"
            "If none of the documents contains the answer, say exactly: I don't have that in my knowledge base.\n\n"
            f"Question: {query}\n\n"
            f"Documents:\n{context}\n\n"
            "Answer:"
        )

        # Invocamos el LLM con el prompt completo.
        # El modelo generará la respuesta basándose únicamente en la evidencia del contexto.
        print("\nRespuesta generada por el LLM:\n", llm.invoke(prompt))


if __name__ == "__main__":
    main()