from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
import asyncio
import chromadb
import httpx
import logging
import os
import re
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from generador_mapas import generar_kml, generar_gpx, extraer_coordenadas, parsear_documento
from ubicacion import lugares_cercanos, texto_a_coordenadas, formatear_respuesta_cercania

load_dotenv()
logging.basicConfig(level=logging.INFO)

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

Si el contexto incluye una línea "[Idioma preferido del usuario: X]", esa
preferencia tiene PRIORIDAD ABSOLUTA sobre la detección automática: responde
siempre en el idioma X, incluso si el mensaje del usuario está escrito en
otro idioma.

FORMATO OBLIGATORIO: Cuando menciones el nombre de un lugar (restaurante, museo, hotel,
parque, etc.), SIEMPRE escríbelo en negritas Markdown: **Nombre del Lugar**.
Esto es obligatorio para todos los nombres propios de lugares. Ejemplo:
- "Te recomiendo **La Bodeguita del Medio**, ubicada en..."
- "El mejor museo es **Museo de la Revolución**"

Usa únicamente la información del contexto proporcionado.
Incluye nombre, dirección, teléfono, calificación y horarios cuando estén disponibles.
Cuando no tengas información exacta de horarios o precios, indícalo claramente
y sugiere confirmar directamente con el lugar.
Recuerda el historial de la conversación para responder preguntas de seguimiento.

REGLA ANTI-ALUCINACIÓN: NUNCA inventes nombres de lugares, direcciones, teléfonos,
horarios, precios ni coordenadas que no aparezcan en el contexto proporcionado.
Si el contexto no contiene lugares relevantes para la pregunta, dilo claramente
("No tengo información sobre eso en mi base de datos") en lugar de improvisar
una recomendación. Es preferible admitir que no tienes el dato a darlo por
inventado."""

Settings.llm = Groq(
    model=GROQ_MODEL,
    api_key=GROQ_KEY,
    request_timeout=60.0
)
Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

chroma_client     = chromadb.PersistentClient(path=DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("lugares_turisticos")
vector_store      = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context   = StorageContext.from_defaults(vector_store=vector_store)
index             = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

# Motores de chat por usuario + timestamp de último uso para TTL
user_chat_engines:     dict = {}
user_engine_last_used: dict = {}


def get_chat_engine(user_id: str):
    if user_id not in user_chat_engines:
        user_chat_engines[user_id] = index.as_chat_engine(
            chat_mode="context",
            verbose=False,
            system_prompt=SYSTEM_PROMPT,
            similarity_top_k=5
        )
    user_engine_last_used[user_id] = datetime.now()
    return user_chat_engines[user_id]


async def _limpiar_engines_loop():
    """Elimina motores de chat inactivos por más de 2 h (corre cada 30 min)."""
    while True:
        await asyncio.sleep(1800)
        ahora     = datetime.now()
        expirados = [
            uid for uid, ts in list(user_engine_last_used.items())
            if ahora - ts > timedelta(hours=2)
        ]
        for uid in expirados:
            user_chat_engines.pop(uid, None)
            user_engine_last_used.pop(uid, None)
        if expirados:
            logging.info(f"TTL cleanup: {len(expirados)} chat engines eliminados")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(_limpiar_engines_loop())
    yield


app = FastAPI(title="Agente Turístico Cuba API", lifespan=lifespan)


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class Pregunta(BaseModel):
    texto: str
    usuario_id: str = "anonimo"
    lat: float = None
    lng: float = None
    idioma: str = None

class ResetRequest(BaseModel):
    usuario_id: str

class SolicitudMapa(BaseModel):
    place_id: str
    nombre: str

class SolicitudMapaMulti(BaseModel):
    nombres: list[str]

class SolicitudCercania(BaseModel):
    lat: float = None
    lng: float = None
    texto_ubicacion: str = None
    usuario_id: str = "anonimo"
    categoria: str = None

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

class BusquedaLugar(BaseModel):
    nombre: str


# ── Helper interno ────────────────────────────────────────────────────────────

def _extraer_campo(texto: str, campo: str) -> str:
    m = re.search(rf"{campo}:\s*(.+)", texto)
    return m.group(1).strip() if m else ""


UMBRAL_RELEVANCIA = 0.5
LOG_PREGUNTAS_SIN_DATOS = "preguntas_sin_datos.log"


def _log_si_sin_contexto(pregunta: str, respuesta_obj):
    """Registra preguntas para las que no se encontró contexto relevante (F9)."""
    try:
        source_nodes = getattr(respuesta_obj, "source_nodes", None) or []
        scores = [getattr(n, "score", None) for n in source_nodes]
        scores = [s for s in scores if s is not None]
        score_max = max(scores) if scores else 0.0

        if score_max < UMBRAL_RELEVANCIA:
            with open(LOG_PREGUNTAS_SIN_DATOS, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()}\tscore={score_max:.3f}\t{pregunta}\n")
    except Exception as e:
        logging.warning(f"No se pudo registrar pregunta sin contexto: {e}")


def _buscar_documentos(nombres: list[str]) -> list[str]:
    """Busca el documento de cada nombre (exact match → fuzzy) y devuelve los encontrados."""
    col         = chroma_client.get_or_create_collection("lugares_turisticos")
    encontrados = []
    todos_cache = None

    for nombre in nombres:
        resultados = col.get(where={"title": nombre})
        if resultados["documents"]:
            encontrados.append(resultados["documents"][0])
            continue

        if todos_cache is None:
            todos_cache = col.get(limit=500)

        nombre_lower = nombre.lower()
        for doc in todos_cache["documents"]:
            if nombre_lower in doc.lower():
                encontrados.append(doc)
                break

    return encontrados


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    try:
        total_lugares = chroma_collection.count()
    except Exception:
        total_lugares = -1
    return {
        "status":          "ok",
        "llm":             GROQ_MODEL,
        "embedding":       EMBED_MODEL,
        "lugares_en_db":   total_lugares,
        "usuarios_activos": len(user_chat_engines)
    }


@app.post("/chat")
async def chat(pregunta: Pregunta, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        engine   = get_chat_engine(pregunta.usuario_id)
        ahora    = datetime.now().strftime("%A %d/%m/%Y %H:%M")
        contexto = f"[Hora actual: {ahora}]"
        if pregunta.lat is not None and pregunta.lng is not None:
            contexto += f"\n[Ubicación GPS actual del usuario: {pregunta.lat}, {pregunta.lng}]"
        if pregunta.idioma:
            contexto += f"\n[Idioma preferido del usuario: {pregunta.idioma}]"
        texto = f"{contexto}\n{pregunta.texto}"

        try:
            respuesta = await engine.achat(texto)
        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "rate limit" in msg or "rate_limit" in msg:
                raise HTTPException(
                    status_code=429,
                    detail="Hemos alcanzado el límite de consultas al asistente. Por favor espera un momento e intenta de nuevo."
                )
            raise

        _log_si_sin_contexto(pregunta.texto, respuesta)

        return {
            "pregunta":   pregunta.texto,
            "respuesta":  str(respuesta),
            "usuario_id": pregunta.usuario_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_chat(solicitud: ResetRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    user_chat_engines.pop(solicitud.usuario_id, None)
    user_engine_last_used.pop(solicitud.usuario_id, None)
    return {"status": "ok", "mensaje": f"Historial de {solicitud.usuario_id} reiniciado"}


@app.post("/buscar_lugar")
async def buscar_lugar_endpoint(solicitud: BusquedaLugar, x_api_key: str = Header(...)):
    """Busca un lugar: exact match → fuzzy → búsqueda vectorial semántica."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        def _buscar_db():
            resultado = chroma_collection.get(where={"title": solicitud.nombre})
            if resultado["documents"]:
                return resultado["metadatas"][0], resultado["documents"][0]
            todos        = chroma_collection.get(limit=500)
            nombre_lower = solicitud.nombre.lower()
            for i, doc in enumerate(todos["documents"]):
                if nombre_lower in doc.lower():
                    return todos["metadatas"][i], doc
            return None, None

        meta, doc = await asyncio.to_thread(_buscar_db)

        if meta is None:
            def _buscar_vectorial():
                retriever = index.as_retriever(similarity_top_k=1)
                nodos     = retriever.retrieve(solicitud.nombre)
                if not nodos:
                    return None, None
                nodo = nodos[0]
                return nodo.metadata, nodo.text

            meta, doc = await asyncio.to_thread(_buscar_vectorial)

        if meta is None or doc is None:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")

        lat, lng = extraer_coordenadas(doc)
        return {
            "nombre":    meta.get("title", solicitud.nombre),
            "thumbnail": meta.get("thumbnail", ""),
            "website":   meta.get("website", ""),
            "lat":       lat,
            "lng":       lng,
            "direccion": _extraer_campo(doc, "Dirección"),
            "telefono":  _extraer_campo(doc, "Teléfono"),
            "rating":    _extraer_campo(doc, "Calificación"),
            "horario":   _extraer_campo(doc, "Horario"),
            "categoria": _extraer_campo(doc, "Categoría de búsqueda"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mapa/kml")
async def descargar_kml(solicitud: SolicitudMapa, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        def _buscar_en_db():
            col        = chroma_client.get_or_create_collection("lugares_turisticos")
            resultados = col.get(where={"title": solicitud.nombre})
            if not resultados["documents"]:
                resultados     = col.get(limit=100)
                docs_filtrados = [d for d in resultados["documents"]
                                  if solicitud.nombre.lower() in d.lower()]
                if not docs_filtrados:
                    return None
                return docs_filtrados[0]
            return resultados["documents"][0]

        texto = await asyncio.to_thread(_buscar_en_db)
        if texto is None:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")

        datos        = parsear_documento(texto)
        lat, lng     = extraer_coordenadas(texto)
        datos["lat"] = lat
        datos["lng"] = lng

        kml            = generar_kml([datos])
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
async def descargar_gpx(solicitud: SolicitudMapa, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        def _buscar_en_db():
            col        = chroma_client.get_or_create_collection("lugares_turisticos")
            resultados = col.get(where={"title": solicitud.nombre})
            if not resultados["documents"]:
                resultados     = col.get(limit=100)
                docs_filtrados = [d for d in resultados["documents"]
                                  if solicitud.nombre.lower() in d.lower()]
                if not docs_filtrados:
                    return None
                return docs_filtrados[0]
            return resultados["documents"][0]

        texto = await asyncio.to_thread(_buscar_en_db)
        if texto is None:
            raise HTTPException(status_code=404, detail="Lugar no encontrado")

        datos        = parsear_documento(texto)
        lat, lng     = extraer_coordenadas(texto)
        datos["lat"] = lat
        datos["lng"] = lng

        gpx            = generar_gpx([datos])
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


@app.post("/mapa/kml_multi")
async def descargar_kml_multi(solicitud: SolicitudMapaMulti, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        textos = await asyncio.to_thread(_buscar_documentos, solicitud.nombres)
        if not textos:
            raise HTTPException(status_code=404, detail="Ningún lugar encontrado")

        lugares = []
        for texto in textos:
            datos = parsear_documento(texto)
            lat, lng = extraer_coordenadas(texto)
            datos["lat"] = lat
            datos["lng"] = lng
            lugares.append(datos)

        kml = generar_kml(lugares)
        return Response(
            content=kml,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": "attachment; filename=lugares_turisticos.kml"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mapa/gpx_multi")
async def descargar_gpx_multi(solicitud: SolicitudMapaMulti, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        textos = await asyncio.to_thread(_buscar_documentos, solicitud.nombres)
        if not textos:
            raise HTTPException(status_code=404, detail="Ningún lugar encontrado")

        lugares = []
        for texto in textos:
            datos = parsear_documento(texto)
            lat, lng = extraer_coordenadas(texto)
            datos["lat"] = lat
            datos["lng"] = lng
            lugares.append(datos)

        gpx = generar_gpx(lugares)
        return Response(
            content=gpx,
            media_type="application/gpx+xml",
            headers={"Content-Disposition": "attachment; filename=lugares_turisticos.gpx"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cercanos")
async def lugares_cercanos_endpoint(solicitud: SolicitudCercania, x_api_key: str = Header(...)):
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
                "lugares":     [],
                "tiene_datos": False
            }

        lugares = await asyncio.to_thread(
            lugares_cercanos, lat, lng, DB_PATH, 3, solicitud.categoria
        )

        DISTANCIA_MAX_KM = 50
        lugares_proximos = [l for l in lugares if l.get("distancia", 999) <= DISTANCIA_MAX_KM]
        respuesta        = formatear_respuesta_cercania(lugares)
        return {
            "respuesta":   respuesta,
            "lugares":     lugares,
            "tiene_datos": bool(lugares_proximos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/buscar_externo")
async def buscar_externo(solicitud: SolicitudBusquedaExterna, x_api_key: str = Header(...)):
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
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
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
async def descargar_kml_externo(solicitud: SolicitudMapaExterno, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        datos = [
            {
                "nombre":    l.nombre, "lat": l.lat, "lng": l.lng,
                "categoria": l.tipo,  "direccion": l.direccion,
                "telefono":  l.telefono, "horario": l.horario, "website": l.website,
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
async def descargar_gpx_externo(solicitud: SolicitudMapaExterno, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        datos = [
            {
                "nombre":    l.nombre, "lat": l.lat, "lng": l.lng,
                "categoria": l.tipo,  "direccion": l.direccion,
                "telefono":  l.telefono, "horario": l.horario, "website": l.website,
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


@app.post("/transcribir")
async def transcribir_audio(audio: UploadFile = File(...), x_api_key: str = Header(...)):
    """Transcribe una nota de voz usando Groq Whisper (gratuito con la misma API key)."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    try:
        contenido = await audio.read()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                files={"file": (audio.filename or "audio.ogg", contenido,
                                 audio.content_type or "audio/ogg")},
                data={"model": "whisper-large-v3-turbo"}
            )
            resp.raise_for_status()
            data = resp.json()

        return {"texto": data.get("text", "").strip()}

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Hemos alcanzado el límite de transcripciones. Intenta de nuevo en unos momentos."
            )
        raise HTTPException(status_code=502, detail=f"Error transcribiendo audio: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
