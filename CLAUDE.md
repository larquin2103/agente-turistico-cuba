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
| `idiomas.py` | Localización del bot — textos de interfaz y etiquetas de tipo en 6 idiomas |
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
| `POST` | `/chat` | Chat RAG con historial por `usuario_id`, con contexto de fecha/hora, GPS e idioma preferido |
| `POST` | `/reset` | Borrar historial de un `usuario_id` |
| `POST` | `/buscar_lugar` | Exact match → fuzzy → vectorial semántico |
| `POST` | `/cercanos` | Lugares cercanos (GPS o nombre de barrio), con filtro opcional de categoría |
| `POST` | `/buscar_externo` | Búsqueda en OpenStreetMap via Overpass API (radio configurable) |
| `POST` | `/mapa/kml` | KML para un lugar en DB |
| `POST` | `/mapa/gpx` | GPX para un lugar en DB |
| `POST` | `/mapa/kml_multi` | KML combinado para varios lugares en DB |
| `POST` | `/mapa/gpx_multi` | GPX combinado para varios lugares en DB |
| `POST` | `/mapa/kml_externo` | KML desde coordenadas directas |
| `POST` | `/mapa/gpx_externo` | GPX desde coordenadas directas |
| `POST` | `/transcribir` | Transcribe notas de voz con Groq Whisper |

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

El paso 3 exige `nodo.score >= UMBRAL_RELEVANCIA` (0.5, mismo umbral que `_log_si_sin_contexto`). Si el score es `None` o está por debajo, se devuelve `None, None` (→ 404) en lugar de la mejor coincidencia disponible. Esto evita mostrar la tarjeta de un lugar de otra ciudad/zona cuando el LLM menciona un sitio que no está en la DB (p. ej. preguntar por Trinidad cuando la DB es de La Habana): es preferible no mostrar tarjeta a mostrar una geográficamente incorrecta.

### Callback de Telegram — límite de 64 bytes

`callback_data` en Telegram tiene límite de 64 bytes. Se usa `callback_store` (dict en memoria) con claves MD5 de 8 caracteres. El formato es `map|<key8chars>`.

TTL de 24 horas — `_limpiar_callback_store()` se llama en cada `guardar_callback()`.

### Rate limiting

`bot.py` implementa sliding window: 5 peticiones por usuario en 60 segundos. Si se supera, el usuario recibe un aviso y la petición se descarta (no llega a Groq).

### TTL de chat engines

Los motores de chat de LlamaIndex se crean por `usuario_id` con `chat_mode="context"` y `similarity_top_k=5` (más contexto recuperado por consulta) y se eliminan tras 2 horas de inactividad. Una tarea de fondo corre cada 30 minutos vía `asyncio.create_task(_limpiar_engines_loop())` iniciada en el `lifespan` de FastAPI.

### Archivos temporales — BytesIO

`manejar_botones()` en `bot.py` usa `io.BytesIO` en lugar de archivos en disco para enviar KML/GPX. Esto evita la condición de carrera cuando dos usuarios piden el mismo archivo al mismo tiempo.

```python
buf      = io.BytesIO(resp.content)
buf.name = f"nombre.{formato}"   # Telegram necesita el atributo name
await query.message.reply_document(document=buf, ...)
```

### Tarjetas visuales — hasta 3 por respuesta

`procesar_pregunta()` en `bot.py` (compartida por `responder()` y `manejar_voz()`) llama `buscar_datos_lugar()` —ahora async, vía `/buscar_lugar`— para los primeros `MAX_TARJETAS * 2 = 6` nombres detectados en la respuesta del LLM y envía tarjeta para los primeros 3 que tengan coordenadas GPS. Si hay más de 1, ofrece un mapa combinado (`/mapa/kml_multi` y `/mapa/gpx_multi`). El mismo patrón de hasta 3 tarjetas + mapa combinado se usa en `manejar_ubicacion()` y en el flujo de cercanía por texto, con todos los lugares devueltos por `/cercanos`.

### Inyección de contexto — fecha/hora, GPS e idioma

`/chat` en `api.py` antepone `[Hora actual: martes 29/05/2026 14:30]` al texto del usuario antes de enviarlo al LLM. Si `bot.py` tiene `lat`/`lng` guardados en `context.user_data` (de un mensaje de ubicación previo), se añaden también como `[Ubicación GPS actual del usuario: lat, lng]`. Si `pregunta.idioma` está presente, se añade `[Idioma preferido del usuario: X]`, que el `SYSTEM_PROMPT` trata con prioridad absoluta sobre la detección automática del idioma del mensaje. Así el LLM responde con conciencia temporal, espacial e idiomática.

### Localización — `idiomas.py` y comando `/idioma`

`idiomas.py` centraliza los textos de interfaz de `bot.py` en 6 idiomas (es/en/it/fr/de/pt):

- `IDIOMAS` — diccionario `{código: {"nombre": ..., "bandera": ...}}`
- `IDIOMA_DEFAULT = "es"`
- `idioma_desde_codigo(codigo)` — normaliza un código BCP47 de Telegram (ej. `"en-US"`) al idioma soportado más cercano, con fallback a `IDIOMA_DEFAULT`
- `t(clave, idioma, **kwargs)` — devuelve el texto traducido para `clave`, con `.format(**kwargs)` para placeholders (`{n}`, `{url}`, `{label}`, etc.) y fallback a español si falta la traducción
- `tipo_label(tipo, idioma)` — traduce los tipos de lugar de OpenStreetMap (restaurant, museum, hotel, etc.)

`obtener_idioma(context, update)` en `bot.py` devuelve `context.user_data["idioma"]` si ya existe; si no, lo detecta de `update.effective_user.language_code` y lo guarda. El comando `/idioma` (`idioma_cmd()`) muestra un teclado inline con las 6 banderas; `manejar_botones()` maneja `callback_data="idioma|<código>"`, guarda la preferencia y confirma en el nuevo idioma. `/reset` preserva `context.user_data["idioma"]` aunque haga `context.user_data.clear()`.

En el flujo RAG, `procesar_pregunta()` envía `payload["idioma"] = IDIOMAS[idioma]["nombre"]` (nombre completo, ej. `"English"`) a `/chat`, reforzando la regla de idioma del `SYSTEM_PROMPT`.

### Detección de nombres de lugares

`detectar_lugares()` en `bot.py` usa 4 patrones regex en cascada:
1. Texto en negritas Markdown `**Nombre**` — el system prompt exige este formato
2. Listas numeradas `1. Nombre`
3. Listas con viñetas `- Nombre`
4. Líneas standalone con mayúscula inicial

El system prompt de `api.py` instruye explícitamente al LLM a usar negritas para nombres de lugares.

### Formato Markdown — negritas del LLM vs. Telegram

El `SYSTEM_PROMPT` instruye al LLM a usar negritas estándar `**Nombre**` (necesario para `detectar_lugares()`), pero el `parse_mode="Markdown"` (legacy) de Telegram solo reconoce negritas con un asterisco: `*Nombre*`. `responder_con_markdown()` en `bot.py` aplica `normalizar_markdown_telegram()` (regex `\*\*(.+?)\*\*` → `*\1*`) **después** de `detectar_lugares()` y antes de enviar la respuesta del LLM con `parse_mode="Markdown"`. Si Telegram rechaza el Markdown resultante (`BadRequest`, p. ej. por asteriscos/guiones bajos sin pareja en el texto del LLM), se reintenta como texto plano. `procesar_pregunta()` usa esta función para la respuesta RAG; las respuestas de `/cercanos` ya usan un solo asterisco (generadas en `ubicacion.py`) y no necesitan normalización.

### Transparencia — sin meta-comentarios del LLM

El `SYSTEM_PROMPT` incluye una "REGLA DE TRANSPARENCIA" que prohíbe al LLM verbalizar su razonamiento interno (p. ej. "Note que cambiaste de idioma", "Por cierto, recuerdo que preguntaste sobre X"). El LLM debe responder directamente a la pregunta, en el idioma correspondiente, sin comentar el contexto, el historial o sus propias instrucciones.

### Mapas combinados multi-lugar

`/mapa/kml_multi` y `/mapa/gpx_multi` reciben una lista de `nombres` y generan un único KML/GPX con todos los lugares encontrados, vía `_buscar_documentos()` (exact match → fuzzy). `manejar_botones()` en `bot.py` hace **una sola llamada** con todos los nombres en lugar de iterar y detenerse en el primer resultado, para que el mapa "combinado" incluya realmente todos los lugares ofrecidos.

### Filtro de categoría en lugares cercanos

`detectar_categoria()` en `bot.py` mapea palabras clave del usuario (en los 6 idiomas soportados) a un filtro de subcadena sobre el campo "Categoría de búsqueda" de cada documento: p. ej. "restaurante"/"food"/"comida" → `"gastronomia"`, "museo"/"museum" → `"tradi"`, "naturaleza"/"parque" → `"natural"`, "auto"/"rentar"/"alquiler" → `"transpor"`, "hotel"/"alojamiento" → `"servicio"`. El filtro se envía como `categoria` en `/cercanos` y se aplica en `lugares_cercanos()` (`ubicacion.py`).

### Regla anti-alucinación

El `SYSTEM_PROMPT` de `api.py` prohíbe explícitamente inventar nombres, direcciones, teléfonos, horarios, precios o coordenadas que no estén en el contexto recuperado. Si no hay contexto relevante para la pregunta, el LLM debe responder "No tengo información sobre eso en mi base de datos" en lugar de improvisar.

### Log de preguntas sin contexto relevante

`_log_si_sin_contexto()` en `api.py` revisa el `score` máximo de los `source_nodes` de cada respuesta del chat engine. Si está por debajo de `UMBRAL_RELEVANCIA = 0.5`, registra la pregunta en `preguntas_sin_datos.log` (timestamp ISO, score, texto) — útil para detectar qué información falta en la base de datos.

### Manejo amigable del límite de Groq (429)

`/chat` y `/transcribir` capturan errores 429 de Groq y responden con `HTTPException(429, ...)` y un mensaje amigable. `procesar_pregunta()` en `bot.py` detecta el status 429 en `httpx.HTTPStatusError` y muestra ese mensaje al usuario en vez de un error genérico.

### Notas de voz (Groq Whisper)

`manejar_voz()` en `bot.py` descarga el audio de Telegram (`voice` o `audio`), lo envía como multipart a `/transcribir` (requiere `python-multipart` en `api.py`), que llama a Groq Whisper (`whisper-large-v3-turbo`, gratuito con la misma API key). El texto transcrito se muestra al usuario y se procesa con `procesar_pregunta()`, igual que un mensaje de texto normal.

### Ampliación de radio en búsqueda externa

`mostrar_resultados_externos()` busca primero en Overpass con un radio de 1 km (`radio_m=1000`). Si no hay resultados, ofrece un botón "🔍 Ampliar búsqueda a 3 km" con `callback_data=f"ampliar|{lat}|{lng}"`, manejado en `manejar_botones()` repitiendo la búsqueda con `radio_m=3000`.

---

## Flujo del usuario GPS

1. Usuario comparte ubicación → `manejar_ubicacion()` (guarda lat/lng en `context.user_data`)
2. Bot llama `/cercanos` con lat/lng
3. Si `tiene_datos=True`: muestra texto, envía hasta `MAX_TARJETAS=3` tarjetas y ofrece KML/GPX combinado de todos los lugares
4. Si `tiene_datos=False`: avisa "no tengo datos de tu zona" → llama `mostrar_resultados_externos()` → Overpass API (radio 1 km) → lista de lugares OSM con Google Maps links por cada uno; si no hay resultados, ofrece botón para ampliar a 3 km

---

## Flujo del usuario texto

1. Usuario escribe pregunta → `responder()` (valida rate limit) → `procesar_pregunta()`
2. Detección de keywords de cercanía en los 6 idiomas soportados ("cerca", "nearby", "più vicino", "près", "in der nähe", "perto", "estoy en", "mi ubicación", etc.)
3. Si es cercanía: usa coords guardadas en `context.user_data` o texto de ubicación, detecta categoría con `detectar_categoria()` → `/cercanos` → hasta 3 tarjetas + mapa combinado
4. Si es RAG: llama `/chat` (con hora actual, GPS e idioma preferido si están disponibles) → LLM responde con negritas en nombres → `detectar_lugares()` → hasta 3 tarjetas con foto, datos, botones Google Maps + KML/GPX, y mapa combinado si hay más de 1
5. Las notas de voz (`manejar_voz()`) se transcriben vía `/transcribir` (Groq Whisper) y siguen el mismo flujo que un mensaje de texto

Todos los textos de la interfaz (botones, mensajes de error, ayuda, emergencia) se obtienen vía `t()` de `idiomas.py` según `obtener_idioma(context, update)`. El usuario puede cambiar su idioma en cualquier momento con `/idioma`.

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

`obtener_place_ids_existentes()` lee los `place_id` ya indexados en ChromaDB antes de cargar; `cargar_carpeta()` calcula este conjunto una sola vez y lo comparte entre archivos, así que cualquier lugar repetido (mismo `place_id`, incluso en archivos distintos) se omite e informa como "Omitidos N lugares duplicados".

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
- No quitar la regla anti-alucinación del `SYSTEM_PROMPT` — evita que el LLM invente lugares, direcciones u horarios fuera del contexto recuperado
