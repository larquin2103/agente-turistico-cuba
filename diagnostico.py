import chromadb
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434"
)

client = chromadb.PersistentClient(path="C:/Users/larquin/agente-turistico/db")
col = client.get_or_create_collection("lugares_turisticos")

print(f"Total documentos: {col.count()}\n")

# Ver todos los documentos con su categoría
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