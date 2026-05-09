from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import chromadb
import re
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from generador_mapas import generar_kml, generar_gpx, extraer_coordenadas, parsear_documento
from ubicacion import lugares_cercanos, texto_a_coordenadas, formatear_respuesta_cercania
import os

API_KEY = "turismo-secret-2024"

Settings.llm = Ollama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    request_timeout=120.0,
    system_prompt="""Eres un agente turístico experto en Cuba, especialmente en La Habana.

REGLA ABSOLUTA DE IDIOMA: Detecta el idioma del mensaje del usuario y responde
SIEMPRE en ese mismo idioma. Sin excepciones.
- Mensaje en inglés → responde en inglés
- Mensaje en italiano → responde en italiano
- Mensaje en francés → responde en francés
- Mensaje en alemán → responde en alemán
- Mensaje en portugués → responde en portugués
- Mensaje en español → responde en español
Nunca respondas en un idioma diferente al que usó el usuario.

Usa únicamente la información del contexto proporcionado.
Incluye nombre, dirección, teléfono, calificación y horarios cuando estén disponibles.
Cuando no tengas información exacta de horarios o precios, indícalo claramente
y sugiere confirmar directamente con el lugar."""
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
query_engine = index.as_query_engine(
    similarity_top_k=10,
    response_mode="compact"
)

app = FastAPI(title="Agente Turístico API")

class Pregunta(BaseModel):
    texto: str
    usuario_id: str = "anonimo"

@app.get("/")
def health():
    return {"status": "ok", "agente": "turístico", "modelo": "qwen2.5:7b"}

@app.post("/chat")
def chat(pregunta: Pregunta, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        respuesta = query_engine.query(pregunta.texto)
        return {
            "pregunta": pregunta.texto,
            "respuesta": str(respuesta),
            "usuario_id": pregunta.usuario_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SolicitudMapa(BaseModel):
    place_id: str
    nombre: str

@app.post("/mapa/kml")
def descargar_kml(solicitud: SolicitudMapa, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        # Buscar el documento en ChromaDB por nombre
        col = chroma_client.get_or_create_collection("lugares_turisticos")
        resultados = col.get(where={"title": solicitud.nombre})

        if not resultados["documents"]:
            # Búsqueda alternativa por texto
            resultados = col.get(limit=100)
            docs_filtrados = [
                d for d in resultados["documents"]
                if solicitud.nombre.lower() in d.lower()
            ]
            if not docs_filtrados:
                raise HTTPException(status_code=404, detail="Lugar no encontrado")
            texto = docs_filtrados[0]
        else:
            texto = resultados["documents"][0]

        datos = parsear_documento(texto)
        lat, lng = extraer_coordenadas(texto)
        datos["lat"] = lat
        datos["lng"] = lng

        kml = generar_kml([datos])
        nombre_archivo = solicitud.nombre.replace(" ", "_")[:30]

        return Response(
            content=kml,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}.kml"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mapa/gpx")
def descargar_gpx(solicitud: SolicitudMapa, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        col = chroma_client.get_or_create_collection("lugares_turisticos")
        resultados = col.get(where={"title": solicitud.nombre})

        if not resultados["documents"]:
            resultados = col.get(limit=100)
            docs_filtrados = [
                d for d in resultados["documents"]
                if solicitud.nombre.lower() in d.lower()
            ]
            if not docs_filtrados:
                raise HTTPException(status_code=404, detail="Lugar no encontrado")
            texto = docs_filtrados[0]
        else:
            texto = resultados["documents"][0]

        datos = parsear_documento(texto)
        lat, lng = extraer_coordenadas(texto)
        datos["lat"] = lat
        datos["lng"] = lng

        gpx = generar_gpx([datos])
        nombre_archivo = solicitud.nombre.replace(" ", "_")[:30]

        return Response(
            content=gpx,
            media_type="application/gpx+xml",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}.gpx"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SolicitudCercania(BaseModel):
    lat: float = None
    lng: float = None
    texto_ubicacion: str = None
    usuario_id: str = "anonimo"

@app.post("/cercanos")
def lugares_cercanos_endpoint(solicitud: SolicitudCercania, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        lat, lng = solicitud.lat, solicitud.lng

        # Si no tiene GPS, intentar resolver desde texto
        if not lat and solicitud.texto_ubicacion:
            lat, lng = texto_a_coordenadas(solicitud.texto_ubicacion)

        if not lat or not lng:
            return {
                "respuesta": (
                    "No pude determinar tu ubicación. "
                    "Comparte tu ubicación GPS con el botón 📎 → Ubicación, "
                    "o escribe el nombre de tu barrio o zona en La Habana."
                ),
                "lugares": []
            }

        lugares = lugares_cercanos(
            lat_usuario=lat,
            lng_usuario=lng,
            db_path="C:/Users/larquin/agente-turistico/db",
            top_n=3
        )

        respuesta = formatear_respuesta_cercania(lugares)
        return {"respuesta": respuesta, "lugares": lugares}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# Agregar también el chroma_client al scope global del api.py
# justo después de crear el index, agregar esta línea:
chroma_client = chromadb.PersistentClient(path="C:/Users/larquin/agente-turistico/db")