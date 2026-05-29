# CLAUDE.md — Agente Turístico Cuba

Guía de referencia para asistentes de IA trabajando en este repositorio.

---

## Resumen del proyecto

Bot de Telegram que actúa como guía turístico de Cuba. Los usuarios escriben en cualquiera de 6 idiomas (español, inglés, italiano, francés, alemán, portugués) y el bot responde usando RAG sobre una base de datos de lugares turísticos, devuelve tarjetas visuales con imagen y botones, genera mapas offline KML/GPX para OsmAnd/Maps.me y busca lugares cercanos por GPS.

**Stack**: python-telegram-bot ≥20 (async) · FastAPI · LlamaIndex · ChromaDB · Groq LLM · HuggingFace Embeddings · httpx

---

## Seguridad — REGLA ABSOLUTA

**NUNCA** hacer commit del archivo `.env`. Contiene `TELEGRAM_TOKEN`, `GROQ_API_KEY` y `API_KEY`.

El `.gitignore` ya lo excluye. Si por error se filtra un token de Telegram, revocarlo inmediatamente en [@BotFather](https://t.me/BotFather) porque cualquiera puede operar el bot con ese token.

---

## Arquitectura

```
Usuario Telegram
      │
      │ python-telegram-bot (polling)
      ▼
bot.py  ────────── httpx async ──────────▶  api.py (FastAPI)
                                                │
                                    ┌───────────┼───────────┐
                                    ▼           ▼           ▼
                               ChromaDB    Groq LLM   Overpass API
                            (vectorial)  (llama-3.1)  (OSM externo)
                                    │
                              LlamaIndex
                           ChatEngine/RAG
                                    │
                           HuggingFace Embed
                          (BAAI/bge-small-en)
```

**Dos procesos separados**: `api.py` y `bot.py` corren en terminales distintas. `bot.py` habla con `api.py` exclusivamente por HTTP.

---

## Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `api.py` | FastAPI backend — RAG, búsqueda, mapas, cercanos, fallback externo |
| `bot.py` | Bot Telegram — handlers, tarjetas, callbacks, rate limiting |
| `ubicacion.py` | Haversine, zonas de La Habana, formato de respuesta cercanos |
| `generador_mapas.py` | Generación KML/GPX compatibles con OsmAnd/Garmin/Google Earth |
| `media.py` | Resolución de imágenes: thumbnail → Wikipedia → Unsplash fallback |
| `cargar_datos.py` | Carga JSONs de Google Maps (SerpAPI) a ChromaDB, deduplica por `place_id` |
| `diagnostico.py` | Muestra documentos indexados en ChromaDB — solo lectura, seguro |
| `test_rag.py` | Pruebas del pipeline RAG — no requiere Telegram |

### Datos

`datos/` contiene archivos JSON de prueba con el formato de Google Maps (SerpAPI). El sistema está diseñado para crecer; estos archivos son solo datos iniciales.

`db/` es la base ChromaDB persistente. No subir a git. Si se corrompe, borrar la carpeta y reejecutar `cargar_datos.py`.

---

## Variables de entorno (`.env`)

```env
TELEGRAM_TOKEN=<token de @BotFather>
API_KEY=turismo-secret-2024          # clave interna bot↔api
DB_PATH=./db                         # ruta ChromaDB
API_URL=http://localhost:8000        # URL de api.py
GROQ_API_KEY=gsk_xxxx               # clave Groq Cloud
GROQ_MODEL=llama-3.1-8b-instant     # modelo LLM
EMBED_MODEL=BAAI/bge-small-en-v1.5  # modelo embeddings (local)
```

Copiar de `.env.example`. Sin comillas en los valores.

---

## Comandos de uso frecuente

```bash
# Instalar dependencias
pip install -r requirements.txt

# Cargar datos turísticos a ChromaDB
python cargar_datos.py datos/

# Ver documentos indexados
python diagnostico.py

# Iniciar API (Terminal 1)
python api.py

# Iniciar bot (Terminal 2)
python bot.py

# Verificar que la API responde
curl http://localhost:8000/

# Limpiar y reindexar ChromaDB (solo si está corrupta)
python -c "
import chromadb
c = chromadb.PersistentClient(path='./db')
c.delete_collection('lugares_turisticos')
"
python cargar_datos.py datos/
```

---

## Endpoints de `api.py`

Todos los endpoints excepto `GET /` requieren el header `x-api-key` con el valor de `API_KEY`.

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Estado: modelo, embeddings, lugares en DB, usuarios activos |
| `POST` | `/chat` | Chat RAG con historial por `usuario_id` |
| `POST` | `/reset` | Borrar historial de un `usuario_id` |
| `POST` | `/buscar_lugar` | Exact match → fuzzy → vectorial semántico |
| `POST` | `/cercanos` | Lugares cercanos (GPS o nombre de barrio) |
| `POST` | `/buscar_externo` | Búsqueda en OpenStreetMap via Overpass API |
| `POST` | `/mapa/kml` | KML para lugar en DB |
| `POST` | `/mapa/gpx` | GPX para lugar en DB |
| `POST` | `/mapa/kml_externo` | KML desde coordenadas directas |
| `POST` | `/mapa/gpx_externo` | GPX desde coordenadas directas |

Documentación interactiva: `http://localhost:8000/docs`

---

## Patrones clave del código

### Concurrencia — async en todo

`api.py` usa `async def` en todos los endpoints. Las operaciones bloqueantes de ChromaDB se envuelven en `asyncio.to_thread()`:

```python
meta, doc = await asyncio.to_thread(_buscar_db)
```

`bot.py` usa `httpx.AsyncClient` para todas las llamadas HTTP. Nunca usar `httpx.Client` síncrono.

### Búsqueda de lugares — 3 niveles

El endpoint `/buscar_lugar` implementa tres pasos en cascada:
1. Exact match por metadata `title`
2. Fuzzy: `nombre.lower() in doc.lower()`
3. Vector similarity via `index.as_retriever(similarity_top_k=1).retrieve(nombre)`

Esto resuelve el caso donde el LLM escribe "Bodeguita del Medio" pero la DB tiene "La Bodeguita del Medio".

### Callback de Telegram — límite de 64 bytes

`callback_data` en Telegram tiene límite de 64 bytes. Se usa `callback_store` (dict en memoria) con claves MD5 de 8 caracteres. El formato es `map|<key8chars>`.

TTL de 24 horas — `_limpiar_callback_store()` se llama en cada `guardar_callback()`.

### Rate limiting

`bot.py` implementa sliding window: 5 peticiones por usuario en 60 segundos. Si se supera, el usuario recibe un aviso y la petición se descarta (no llega a Groq).

### TTL de chat engines

Los motores de chat de LlamaIndex se crean por `usuario_id` y se eliminan tras 2 horas de inactividad. Una tarea de fondo corre cada 30 minutos vía `asyncio.create_task(_limpiar_engines_loop())` iniciada en el `lifespan` de FastAPI.

### Archivos temporales — BytesIO

`manejar_botones()` en `bot.py` usa `io.BytesIO` en lugar de archivos en disco para enviar KML/GPX. Esto evita la condición de carrera cuando dos usuarios piden el mismo archivo al mismo tiempo.

```python
buf      = io.BytesIO(resp.content)
buf.name = f"nombre.{formato}"   # Telegram necesita el atributo name
await query.message.reply_document(document=buf, ...)
```

### Tarjetas visuales — hasta 3 por respuesta

`responder()` en `bot.py` llama `buscar_datos_lugar()` para los primeros `MAX_TARJETAS * 2 = 6` nombres detectados en la respuesta del LLM y envía tarjeta para los primeros 3 que tengan coordenadas GPS en la DB. Si hay más de 1, ofrece un mapa combinado.

### Inyección de fecha/hora

`/chat` en `api.py` antepone `[Hora actual: martes 29/05/2026 14:30]` al texto del usuario antes de enviarlo al LLM. Así el LLM puede responder preguntas sobre horarios con conciencia temporal.

### Detección de nombres de lugares

`detectar_lugares()` en `bot.py` usa 4 patrones regex en cascada:
1. Texto en negritas Markdown `**Nombre**` — el system prompt exige este formato
2. Listas numeradas `1. Nombre`
3. Listas con viñetas `- Nombre`
4. Líneas standalone con mayúscula inicial

El system prompt de `api.py` instruye explícitamente al LLM a usar negritas para nombres de lugares.

---

## Flujo del usuario GPS

1. Usuario comparte ubicación → `manejar_ubicacion()`
2. Bot llama `/cercanos` con lat/lng
3. Si `tiene_datos=True`: muestra texto, envía tarjeta del primer lugar, ofrece KML/GPX combinado
4. Si `tiene_datos=False`: avisa "no tengo datos de tu zona" → llama `mostrar_resultados_externos()` → Overpass API → lista de lugares OSM con Google Maps links por cada uno

---

## Flujo del usuario texto

1. Usuario escribe pregunta → `responder()`
2. Detección de keywords de cercanía ("cerca", "nearby", etc.)
3. Si es cercanía: usa coords guardadas en `context.user_data` o texto de ubicación → `/cercanos`
4. Si es RAG: llama `/chat` → LLM responde con negritas en nombres → `detectar_lugares()` → hasta 3 tarjetas con foto, datos, botones Google Maps + KML/GPX

---

## Límites del plan gratuito de Groq

| Límite | Valor |
|---|---|
| Solicitudes por minuto | 30 |
| Tokens por minuto | 131,072 |
| Solicitudes por día | 14,400 |
| Reset diario | 00:00 UTC |

El rate limiting en `bot.py` (5 req/60s/usuario) protege la cuota de Groq ante usuarios abusivos.

---

## Formato JSON de datos turísticos

Los archivos en `datos/` siguen el formato de Google Maps exportado por SerpAPI. Campos relevantes que usa `cargar_datos.py`:

- `place_id` — identificador único para deduplicación
- `title` — nombre del lugar (guardado como metadata `title`)
- `address` — dirección
- `phone` — teléfono
- `rating` — calificación
- `hours` — horario
- `website` — sitio web
- `thumbnail` — URL de imagen de preview
- `gps_coordinates.latitude` / `gps_coordinates.longitude`
- `type` / `types` — categoría

`cargar_datos.py` construye un texto estructurado con etiquetas `Nombre: X\nDirección: Y\n...` que `ubicacion.py` y `api.py` parsean con regex. Añadir nuevos lugares: copiar JSON en `datos/` y correr `python cargar_datos.py datos/nuevo.json`, luego reiniciar `api.py`.

---

## Lo que NO hacer

- No usar `def` síncrono en endpoints de FastAPI — bloquea el event loop bajo carga
- No crear `chromadb.PersistentClient` dentro de handlers o por llamada — crear a nivel de módulo
- No escribir archivos temporales en disco para KML/GPX — usar `io.BytesIO`
- No hacer commit de `.env` bajo ninguna circunstancia
- No subir la carpeta `db/` a git — puede pesar varios GB
- No hardcodear `API_KEY` ni tokens en el código — siempre via `os.getenv()`
- No usar `httpx.Client` síncrono en código async — siempre `httpx.AsyncClient`
- No reiniciar solo el bot cuando se añaden datos nuevos — hay que reiniciar `api.py` (tiene el índice en memoria)
