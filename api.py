from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import chromadb
import httpx
import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from generador_mapas import generar_kml, generar_gpx, extraer_coordenadas, parsear_documento
from ubicacion import lugares_cercanos, texto_a_coordenadas, formatear_respuesta_cercania

load_dotenv()

API_KEY     = os.getenv("API_KEY")
DB_PATH     = os.getenv("DB_PATH", "./db")
GROQ_KEY    = os.getenv("GROQ_API_KEY")
GROQ_MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

SYSTEM_PROMPT = """Eres un agente turístico experto en Cuba, especialmente en La Habana.

REGLA ABSOLUTA DE IDIOMA: Detecta el idioma del mensaje del usuario y responde
SIEMPRE en ese mismo idioma. Sin excepciones.
- Mensaje en inglés → responde en inglés
- Mensaje en italiano → responde en italiano
- Mensaje en francés → responde en francés
- Mensaje en alemán → responde en alemán
- Mensaje en portugués → responde en portugués
- Mensaje en español → responde en español
Nunca respondas en un idioma diferente al que usó el usuario.

FORMATO OBLIGATORIO: Cuando menciones el nombre de un lugar (restaurante, museo, hotel,
parque, etc.), SIEMPRE escríbelo en negritas Markdown: **Nombre del Lugar**.
Esto es obligatorio para todos los nombres propios de lugares. Ejemplo:
- "Te recomiendo **La Bodeguita del Medio**, ubicada en..."
- "El mejor museo es **Museo de la Revolución**"

Usa únicamente la información del contexto proporcionado.
Incluye nombre, dirección, teléfono, calificación y horarios cuando estén disponibles.
Cuando no tengas información exacta de horarios o precios, indícalo claramente
y sugiere confirmar directamente con el lugar.
Recuerda el historial de la conversación para responder preguntas de seguimiento."""

Settings.llm = Groq(
    model=GROQ_MODEL,
    api_key=GROQ_KEY,
    request_timeout=60.0
)
Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

chroma_client = chromadb.PersistentClient(path=DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("lugares_turisticos")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

# Motor de chat con historial por usuario
user_chat_engines: dict = {}

def get_chat_engine(user_id: str):
    if user_id not in user_chat_engines:
        user_chat_engines[user_id] = index.as_chat_engine(
            chat_mode="context",
            verbose=False,
            system_prompt=SYSTEM_PROMPT
        )
    return user_chat_engines[user_id]

app = FastAPI(title="Agente Turístico Cuba API")

class Pregunta(BaseModel):
    texto: str
    usuario_id: str = "anonimo"

class ResetRequest(BaseModel):
    usuario_id: str

class SolicitudMapa(BaseModel):
    place_id: str
    nombre: str

class SolicitudCercania(BaseModel):
    lat: float = None
    lng: float = None
    texto_ubicacion: str = None
    usuario_id: str = "anonimo"

class SolicitudBusquedaExterna(BaseModel):
    lat: float
    lng: float
    radio_m: int = 1000

class LugarExterno(BaseModel):
    nombre: str
    lat: float
    lng: float
    tipo: str = ""
    direccion: str = ""
    telefono: str = ""
    horario: str = ""
    website: str = ""

class SolicitudMapaExterno(BaseModel):
    lugares: list[LugarExterno]


@app.get("/")
def health():
    try:
        total_lugares = chroma_collection.count()
    except Exception:
        total_lugares = -1
    return {
        "status": "ok",
        "llm": GROQ_MODEL,
        "embedding": EMBED_MODEL,
        "lugares_en_db": total_lugares,
        "usuarios_activos": len(user_chat_engines)
    }


@app.post("/chat")
def chat(pregunta: Pregunta, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        engine = get_chat_engine(pregunta.usuario_id)
        respuesta = engine.chat(pregunta.texto)
        return {
            "pregunta": pregunta.texto,
            "respuesta": str(respuesta),
            "usuario_id": pregunta.usuario_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
def reset_chat(solicitud: ResetRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    user_chat_engines.pop(solicitud.usuario_id, None)
    return {"status": "ok", "mensaje": f"Historial de {solicitud.usuario_id} reiniciado"}


@app.post("/mapa/kml")
def descargar_kml(solicitud: SolicitudMapa, x_api_key: str = Header(...)):
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


@app.post("/cercanos")
def lugares_cercanos_endpoint(solicitud: SolicitudCercania, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        lat, lng = solicitud.lat, solicitud.lng

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
            db_path=DB_PATH,
            top_n=3
        )

        DISTANCIA_MAX_KM = 50
        lugares_proximos = [l for l in lugares if l.get("distancia", 999) <= DISTANCIA_MAX_KM]
        respuesta = formatear_respuesta_cercania(lugares)
        return {
            "respuesta": respuesta,
            "lugares": lugares,
            "tiene_datos": bool(lugares_proximos)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/buscar_externo")
def buscar_externo(solicitud: SolicitudBusquedaExterna, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")

    query = (
        f"[out:json][timeout:10];"
        f"("
        f'node["amenity"~"restaurant|cafe|bar|pub|fast_food|museum|hotel|hostel|guest_house|theatre|cinema|pharmacy|bank"]'
        f"(around:{solicitud.radio_m},{solicitud.lat},{solicitud.lng});"
        f'node["tourism"~"hotel|hostel|museum|attraction|viewpoint|gallery|information|apartment"]'
        f"(around:{solicitud.radio_m},{solicitud.lat},{solicitud.lng});"
        f'node["historic"]'
        f"(around:{solicitud.radio_m},{solicitud.lat},{solicitud.lng});"
        f");"
        f"out body;"
    )

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(
                "https://overpass-api.de/api/interpreter",
                params={"data": query}
            )
            resp.raise_for_status()

        from ubicacion import haversine

        lugares = []
        for elem in resp.json().get("elements", []):
            tags = elem.get("tags", {})
            name = (tags.get("name") or tags.get("name:es") or
                    tags.get("name:en") or tags.get("name:fr"))
            if not name:
                continue

            dist = haversine(solicitud.lat, solicitud.lng, elem["lat"], elem["lon"])
            tipo = (tags.get("amenity") or tags.get("tourism") or
                    tags.get("historic") or "lugar")

            calle     = tags.get("addr:street", "")
            numero    = tags.get("addr:housenumber", "")
            direccion = f"{calle} {numero}".strip() if calle else ""

            lugares.append({
                "nombre":    name,
                "tipo":      tipo,
                "lat":       elem["lat"],
                "lng":       elem["lon"],
                "distancia": round(dist, 3),
                "direccion": direccion,
                "telefono":  tags.get("phone", tags.get("contact:phone", "")),
                "horario":   tags.get("opening_hours", ""),
                "website":   tags.get("website", tags.get("contact:website", "")),
            })

        lugares.sort(key=lambda x: x["distancia"])
        return {"lugares": lugares[:10], "fuente": "OpenStreetMap", "total": len(lugares)}

    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Timeout en búsqueda externa")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mapa/kml_externo")
def descargar_kml_externo(solicitud: SolicitudMapaExterno, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        datos = [
            {
                "nombre":    l.nombre,
                "lat":       l.lat,
                "lng":       l.lng,
                "categoria": l.tipo,
                "direccion": l.direccion,
                "telefono":  l.telefono,
                "horario":   l.horario,
                "website":   l.website,
            }
            for l in solicitud.lugares
        ]
        kml = generar_kml(datos)
        return Response(
            content=kml,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": "attachment; filename=lugares_cercanos.kml"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mapa/gpx_externo")
def descargar_gpx_externo(solicitud: SolicitudMapaExterno, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        datos = [
            {
                "nombre":    l.nombre,
                "lat":       l.lat,
                "lng":       l.lng,
                "categoria": l.tipo,
                "direccion": l.direccion,
                "telefono":  l.telefono,
                "horario":   l.horario,
                "website":   l.website,
            }
            for l in solicitud.lugares
        ]
        gpx = generar_gpx(datos)
        return Response(
            content=gpx,
            media_type="application/gpx+xml",
            headers={"Content-Disposition": "attachment; filename=lugares_cercanos.gpx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
