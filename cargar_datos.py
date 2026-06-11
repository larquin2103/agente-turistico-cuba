import json
import os
import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

DB_PATH     = os.getenv("DB_PATH", "./db")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# Solo necesitamos embeddings para indexar (el LLM no se usa aquí)
Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

chroma_client = chromadb.PersistentClient(path=DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("lugares_turisticos")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

def construir_texto(lugar: dict) -> str:
    partes = []

    if lugar.get("title"):
        partes.append(f"Nombre: {lugar['title']}")
    if lugar.get("address"):
        partes.append(f"Dirección: {lugar['address']}")
    if lugar.get("phone"):
        partes.append(f"Teléfono: {lugar['phone']}")
    if lugar.get("rating"):
        partes.append(f"Calificación: {lugar['rating']} estrellas")
    if lugar.get("reviews"):
        partes.append(f"Reseñas: {lugar['reviews']} opiniones de turistas")
    if lugar.get("website"):
        partes.append(f"Sitio web: {lugar['website']}")
    if lugar.get("type"):
        partes.append(f"Tipo: {lugar['type']}")
    if lugar.get("types"):
        partes.append(f"Categorías: {', '.join(lugar['types'])}")
    if lugar.get("description"):
        partes.append(f"Descripción: {lugar['description']}")
    if lugar.get("hours"):
        horario = lugar["hours"]
        if isinstance(horario, list):
            partes.append(f"Horario: {', '.join(horario)}")
        else:
            partes.append(f"Horario: {horario}")
    if lugar.get("price"):
        partes.append(f"Precio: {lugar['price']}")
    if lugar.get("gps_coordinates"):
        coords = lugar["gps_coordinates"]
        lat = coords.get("latitude", "")
        lng = coords.get("longitude", "")
        partes.append(f"Coordenadas GPS: {lat}, {lng}")

    query = lugar.get("_query", "")
    if query:
        partes.append(f"Categoría de búsqueda: {query}")

    return "\n".join(partes)

def construir_metadata(lugar: dict) -> dict:
    return {
        "place_id":  lugar.get("place_id", ""),
        "title":     lugar.get("title", ""),
        "rating":    str(lugar.get("rating", "")),
        "address":   lugar.get("address", ""),
        "position":  str(lugar.get("position", "")),
        "thumbnail": lugar.get("thumbnail", ""),
        "website":   lugar.get("website", ""),
        "lat":       str(lugar.get("gps_coordinates", {}).get("latitude", "")),
        "lng":       str(lugar.get("gps_coordinates", {}).get("longitude", "")),
    }

def obtener_place_ids_existentes() -> set:
    """Devuelve el conjunto de place_id ya indexados en ChromaDB."""
    try:
        existentes = chroma_collection.get()
        return {
            m.get("place_id", "") for m in existentes.get("metadatas", [])
            if m and m.get("place_id")
        }
    except Exception:
        return set()

def cargar_json(ruta_archivo: str, place_ids_existentes: set = None):
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        data = json.load(f)

    query = data.get("query", "")
    location = data.get("location", "")
    lugares = data.get("local_results", [])

    print(f"\nArchivo: {ruta_archivo}")
    print(f"Query: {query}")
    print(f"Ubicación: {location}")
    print(f"Lugares encontrados: {len(lugares)}")

    if place_ids_existentes is None:
        place_ids_existentes = obtener_place_ids_existentes()

    documentos = []
    omitidos = 0
    for lugar in lugares:
        place_id = lugar.get("place_id", "")
        if place_id and place_id in place_ids_existentes:
            omitidos += 1
            continue

        lugar["_query"] = query
        texto = construir_texto(lugar)
        if texto.strip():
            doc = Document(
                text=texto,
                metadata=construir_metadata(lugar)
            )
            documentos.append(doc)
            if place_id:
                place_ids_existentes.add(place_id)

    if omitidos:
        print(f"Omitidos {omitidos} lugares duplicados (ya indexados por place_id)")

    if documentos:
        print(f"Indexando {len(documentos)} lugares...")
        index = VectorStoreIndex.from_documents(
            documentos,
            storage_context=storage_context
        )
        print(f"✓ {len(documentos)} lugares indexados correctamente")
    else:
        print("No se encontraron lugares nuevos para indexar en este archivo")

    return len(documentos)

def cargar_carpeta(ruta_carpeta: str):
    archivos = [
        f for f in os.listdir(ruta_carpeta)
        if f.endswith(".json")
    ]

    if not archivos:
        print(f"No se encontraron archivos JSON en {ruta_carpeta}")
        return

    print(f"Encontrados {len(archivos)} archivos JSON")
    place_ids_existentes = obtener_place_ids_existentes()
    total = 0
    for archivo in archivos:
        ruta = os.path.join(ruta_carpeta, archivo)
        total += cargar_json(ruta, place_ids_existentes)

    print(f"\n✓ TOTAL: {total} lugares indexados en ChromaDB")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso:")
        print("  Un archivo:  python cargar_datos.py datos/gastronomia.json")
        print("  Una carpeta: python cargar_datos.py datos/")
        sys.exit(1)

    ruta = sys.argv[1]

    if os.path.isdir(ruta):
        cargar_carpeta(ruta)
    elif os.path.isfile(ruta):
        cargar_json(ruta)
    else:
        print(f"No se encontró: {ruta}")
