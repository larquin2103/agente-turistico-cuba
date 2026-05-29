import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

load_dotenv()

DB_PATH     = os.getenv("DB_PATH", "./db")
GROQ_KEY    = os.getenv("GROQ_API_KEY")
GROQ_MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

Settings.llm = Groq(model=GROQ_MODEL, api_key=GROQ_KEY, request_timeout=60.0)
Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

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
