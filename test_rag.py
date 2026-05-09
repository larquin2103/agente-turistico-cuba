from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

Settings.llm = Ollama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    request_timeout=120.0,
    system_prompt="Eres un agente turístico experto en Cuba, especialmente en La Habana. Responde SIEMPRE en español. Usa únicamente la información del contexto proporcionado. Incluye detalles como dirección, teléfono, calificación y horarios cuando los tengas disponibles."
)
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)

chroma_client = chromadb.PersistentClient(path="C:/Users/larquin/agente-turistico/db")
chroma_collection = chroma_client.get_or_create_collection("lugares_turisticos")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
query_engine = index.as_query_engine(similarity_top_k=3)

print("\n--- AGENTE TURÍSTICO CUBA LISTO ---\n")

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