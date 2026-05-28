import chromadb
import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

DB_PATH     = os.getenv("DB_PATH", "./db")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

client = chromadb.PersistentClient(path=DB_PATH)
col = client.get_or_create_collection("lugares_turisticos")

print(f"Total documentos: {col.count()}\n")

todos = col.get()
categorias = {}
for doc in todos["documents"]:
    lineas = doc.split("\n")
    categoria = "sin categoria"
    nombre = "sin nombre"
    for linea in lineas:
        if linea.startswith("Categoría de búsqueda:"):
            categoria = linea.replace("Categoría de búsqueda:", "").strip()
        if linea.startswith("Nombre:"):
            nombre = linea.replace("Nombre:", "").strip()
    if categoria not in categorias:
        categorias[categoria] = []
    categorias[categoria].append(nombre)

print("=== DOCUMENTOS POR CATEGORÍA ===")
for cat, nombres in categorias.items():
    print(f"\n[{cat}] — {len(nombres)} lugares")
    for n in nombres[:5]:
        print(f"  - {n}")
    if len(nombres) > 5:
        print(f"  ... y {len(nombres)-5} más")
