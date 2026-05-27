import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

load_dotenv()

DB_PATH      = os.getenv("DB_PATH", "./db")
OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

Settings.llm = Ollama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    request_timeout=120.0,
    system_prompt=(
        "Eres un agente turístico experto en Cuba, especialmente en La Habana. "
        "Responde SIEMPRE en español. Usa únicamente la información del contexto "
        "proporcionado. Incluye detalles como dirección, teléfono, calificación "
        "y horarios cuando los tengas disponibles."
    )
)
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url=OLLAMA_URL
)

chroma_client = chromadb.PersistentClient(path=DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("lugares_turisticos")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
query_engine = index.as_query_engine(similarity_top_k=3)

print(f"\n--- AGENTE TURÍSTICO CUBA LISTO ({chroma_collection.count()} lugares en DB) ---\n")

preguntas = [
    "¿Cuál es el mejor restaurante en La Habana según las reseñas?",
    "¿Dónde puedo rentar un auto en La Habana?",
    "¿Qué lugares naturales puedo visitar en Cuba?",
    "¿Qué sitios culturales y de tradiciones hay en La Habana?",
    "¿Dónde puedo conseguir transporte turístico en Cuba?",
]

for pregunta in preguntas:
    print(f"Pregunta: {pregunta}")
    respuesta = query_engine.query(pregunta)
    print(f"Respuesta: {respuesta}\n")
    print("-" * 60 + "\n")
