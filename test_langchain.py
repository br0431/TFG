from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# Ejemplo de documento
doc = "Lux es carry AP con Blue Buff en TFT Set 16"

# Dividir el texto en chunks de 50 caracteres y que se solapan 10 con el anterior chunk (para no cortar las ideas)
splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
chunks = splitter.split_text(doc)

# Generador de embeddings en base al modelo
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Meter los chunks en chroma, recorre cada texto en chunks y para cada uno obtiene un embedding, crea una db local y guarda el chunk, su embedding y un id
db = Chroma.from_texts(chunks, embedder)

# Ejemplo de query/pregunta del usuario
query = "¿Quién usa Blue Buff?"
# Internamente se genera el embedding de la query usando embedder, se compara el vector con todos los guardados en chroma, se ordenan por mayor similitud y devuelven los k más similares
result = db.similarity_search(query, k=2)
print(result)
