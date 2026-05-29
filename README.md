# Agente Turístico Cuba 🇨🇺

Asistente turístico inteligente para Cuba accesible desde **Telegram**. Combina RAG (Retrieval-Augmented Generation) sobre una base de datos local de lugares turísticos con el LLM de Groq en la nube para responder preguntas en 6 idiomas, recomendar lugares con tarjetas visuales, generar mapas offline (KML/GPX) y buscar lugares cercanos por GPS.

---

## Arquitectura

```
Telegram Bot (bot.py)
       │
       │  HTTP async (httpx)
       ▼
FastAPI Backend (api.py)  ←→  ChromaDB (./db)
       │                           │
       │                     LlamaIndex RAG
       ▼                           │
  Groq LLM                  HuggingFace Embeddings
(llama-3.1-8b-instant)    (BAAI/bge-small-en-v1.5)
       │
       ▼ (fallback externo)
  Overpass API (OpenStreetMap)
```

---

## Características

| Funcionalidad | Detalle |
|---|---|
| 🌍 **Multilingüe** | Español, inglés, italiano, francés, alemán, portugués — autodetección |
| 🤖 **RAG con historial** | Conversación con contexto por usuario (LlamaIndex ChatEngine) |
| 📍 **GPS cercanos** | Top 3 lugares más cercanos al compartir ubicación |
| 🔍 **Fallback externo** | OpenStreetMap/Overpass cuando no hay datos locales |
| 🗺️ **Mapas offline** | KML y GPX para OsmAnd y Maps.me (sin internet) |
| 📍 **Google Maps** | Enlace directo por cada lugar para navegación inmediata |
| 🖼️ **Tarjetas visuales** | Hasta 3 tarjetas con imagen, datos y botones por recomendación |
| 🕐 **Conciencia temporal** | Hora/fecha actual inyectada en cada consulta al LLM |
| 🆘 **Emergencias** | Comando `/emergencia` con números útiles en Cuba |
| ⚡ **Concurrencia** | Endpoints async, rate limiting 5 req/60s por usuario |

---

## Estructura del proyecto

```
agente-turistico-cuba/
│
├── api.py              # FastAPI backend — RAG, mapas, búsqueda
├── bot.py              # Bot Telegram — handlers, tarjetas, callbacks
├── ubicacion.py        # Haversine, zonas de La Habana, formato cercanos
├── generador_mapas.py  # Generación KML/GPX compatible OsmAnd/Garmin
├── media.py            # Imágenes: thumbnail → Wikipedia → Unsplash
├── cargar_datos.py     # Cargador de JSONs a ChromaDB
├── diagnostico.py      # Ver documentos indexados en ChromaDB
├── test_rag.py         # Pruebas del pipeline RAG
│
├── datos/              # JSONs con lugares turísticos (datos de prueba)
│   ├── Cultura.json
│   ├── havanaGst.json
│   ├── Naturale.json
│   ├── Servicion.json
│   └── transpor.json
│
├── db/                 # ChromaDB persistente — NO borrar ni subir a git
├── .env                # Credenciales — NO subir a git (ver .env.example)
├── .env.example        # Plantilla de configuración
└── requirements.txt    # Dependencias Python
```

---

## Requisitos

- Python 3.9 o superior (probado con 3.13)
- Cuenta en [Groq](https://console.groq.com) — API key gratuita
- Bot de Telegram creado con [@BotFather](https://t.me/BotFather)

---

## Instalación

### 1 — Clonar el repositorio

```bash
git clone https://github.com/larquin2103/agente-turistico-cuba.git
cd agente-turistico-cuba
```

### 2 — Crear entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

Si da error de permisos, ejecutar una sola vez:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3 — Instalar dependencias

```bash
pip install -r requirements.txt
```

> La primera vez descarga el modelo de embeddings (~130 MB). Solo ocurre una vez.

### 4 — Configurar credenciales

Copiar la plantilla y rellenar con valores reales:

```bash
cp .env.example .env
```

Editar `.env`:

```env
TELEGRAM_TOKEN=tu_token_de_botfather
API_KEY=turismo-secret-2024
DB_PATH=./db
API_URL=http://localhost:8000
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.1-8b-instant
EMBED_MODEL=BAAI/bge-small-en-v1.5
```

> Las API keys van **sin comillas** en el archivo `.env`.

### 5 — Cargar datos turísticos

```bash
python cargar_datos.py datos/
```

Verifica cuántos documentos se indexaron:

```bash
python diagnostico.py
```

---

## Ejecución

Necesitas **dos terminales** con el entorno virtual activado:

**Terminal 1 — API:**
```bash
python api.py
```
Esperar hasta ver `Application startup complete.`

**Terminal 2 — Bot:**
```bash
python bot.py
```
Esperar hasta ver `Bot corriendo...`

### Verificar que la API responde

```bash
curl http://localhost:8000/
```

Respuesta esperada:
```json
{
  "status": "ok",
  "llm": "llama-3.1-8b-instant",
  "embedding": "BAAI/bge-small-en-v1.5",
  "lugares_en_db": 81,
  "usuarios_activos": 0
}
```

**En Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/" | Select-Object -ExpandProperty Content
```

---

## Uso del bot en Telegram

| Comando / Acción | Resultado |
|---|---|
| `/start` | Bienvenida multilingüe + botón de ubicación |
| `/ayuda` | Lista completa de funciones |
| `/reset` | Borra el historial de conversación |
| `/emergencia` | Números de urgencia en Cuba |
| Texto libre | Respuesta RAG en el idioma del mensaje |
| Compartir ubicación | Top 3 lugares cercanos con tarjeta y mapa |
| Botón "📍 Ver en Google Maps" | Abre Google Maps con la ubicación exacta |
| Botón "🗺️ KML offline" | Descarga mapa para OsmAnd / Maps.me |
| Botón "📍 GPX offline" | Descarga mapa para OsmAnd / Garmin |

### Ejemplos de preguntas

```
¿Cuál es el mejor restaurante en La Habana Vieja?
Best museums in Havana
Dove posso mangiare vicino al Capitolio?
Melhores hotéis em Havana
Was sind die besten Sehenswürdigkeiten?
Quels restaurants recommandes-tu à La Havane?
```

---

## Agregar nuevos datos turísticos

Los datos se cargan desde archivos JSON con el formato de Google Maps (SerpAPI). Los archivos en `datos/` son de prueba — el sistema está diseñado para crecer.

**Cargar un archivo:**
```bash
python cargar_datos.py datos/nuevo_archivo.json
```

**Cargar toda la carpeta:**
```bash
python cargar_datos.py datos/
```

El sistema detecta duplicados por `place_id` — cargar el mismo archivo dos veces no genera duplicados.

Después de cargar datos nuevos **reiniciar la API** para que el índice vectorial los incluya:
```bash
# Ctrl+C en la terminal de api.py y volver a ejecutar
python api.py
```

---

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Estado del sistema |
| `POST` | `/chat` | Chat RAG con historial por usuario |
| `POST` | `/reset` | Borrar historial de un usuario |
| `POST` | `/buscar_lugar` | Buscar lugar en DB (exact → fuzzy → vectorial) |
| `POST` | `/cercanos` | Lugares cercanos por GPS o nombre de zona |
| `POST` | `/buscar_externo` | Búsqueda en OpenStreetMap (Overpass API) |
| `POST` | `/mapa/kml` | Generar KML para lugar en DB |
| `POST` | `/mapa/gpx` | Generar GPX para lugar en DB |
| `POST` | `/mapa/kml_externo` | Generar KML desde coordenadas directas |
| `POST` | `/mapa/gpx_externo` | Generar GPX desde coordenadas directas |

Documentación interactiva: `http://localhost:8000/docs`

---

## Diagnóstico y resolución de problemas

### Ver documentos en ChromaDB
```bash
python diagnostico.py
```

### Limpiar y reindexar ChromaDB
Solo si los datos están corruptos:
```bash
python -c "
import chromadb
c = chromadb.PersistentClient(path='./db')
c.delete_collection('lugares_turisticos')
print('Colección eliminada')
"
python cargar_datos.py datos/
```

### Error: modelo Groq no disponible
Cambiar `GROQ_MODEL` en `.env` a uno disponible en tu plan:
```
GROQ_MODEL=llama-3.1-8b-instant
```

### El bot se queda sin responder
- Verificar que la API está corriendo en Terminal 1
- Revisar logs en ambas terminales
- Comprobar que `API_URL=http://localhost:8000` en `.env`

---

## Configuración de referencia

| Parámetro | Valor por defecto | Descripción |
|---|---|---|
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Modelo LLM en Groq |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | Modelo de embeddings local |
| `DB_PATH` | `./db` | Ruta de ChromaDB |
| `API_URL` | `http://localhost:8000` | URL interna de la API |
| `API_KEY` | `turismo-secret-2024` | Clave de autenticación interna |
| Rate limit | 5 req / 60 s / usuario | Protege la quota de Groq |
| TTL callbacks | 24 h | Tiempo de vida de botones de mapa |
| TTL chat engines | 2 h sin actividad | Limpieza de historial en memoria |

---

## Límites del plan gratuito de Groq

| Límite | Valor |
|---|---|
| Solicitudes por minuto | 30 |
| Tokens por minuto | 131,072 |
| Solicitudes por día | 14,400 |
| Reset diario | 00:00 UTC |

14,400 req/día equivale a ~10 preguntas/minuto sostenidas las 24 h — suficiente para demo y uso moderado con múltiples usuarios.

---

## Próximos pasos

- [ ] Ampliar base de datos: Trinidad, Varadero, Viñales, Santiago de Cuba
- [ ] Reconocimiento de voz multilingüe (Groq Whisper — mismo API key)
- [ ] Síntesis de voz en respuestas (edge-tts, gratuito)
- [ ] Panel de administración web para cargar datos sin línea de comandos
- [ ] Persistencia de historial en Redis (para sobrevivir reinicios)
- [ ] Despliegue en VPS para disponibilidad 24/7
- [ ] WhatsApp Business API como canal adicional
