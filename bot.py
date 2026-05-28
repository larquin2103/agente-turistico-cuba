import logging
import re
import os
import asyncio
import hashlib
import httpx
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURACIÓN — leída desde .env
# ─────────────────────────────────────────────
PROXY_URL = os.getenv("PROXY_URL", "")
TOKEN     = os.getenv("TELEGRAM_TOKEN")
API_URL   = os.getenv("API_URL", "http://localhost:8000")
API_KEY   = os.getenv("API_KEY")
DB_PATH   = os.getenv("DB_PATH", "./db")
# ─────────────────────────────────────────────

# localhost nunca usa proxy
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

import chromadb
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from media import obtener_imagen, construir_caption

logging.basicConfig(level=logging.INFO)

# Almacena el último lugar mencionado por usuario {usuario_id: nombre_lugar}
ultimos_lugares = {}

# Almacén de callbacks — evita superar el límite de 64 bytes de Telegram
# {clave_corta: {"formato": "kml"/"gpx", "nombres": [...]}}
callback_store: dict = {}

def guardar_callback(formato: str, nombres: list) -> str:
    """Guarda nombres de lugares de BD y devuelve clave ≤8 chars para callback_data."""
    key = hashlib.md5(f"{formato}{'|'.join(nombres)}".encode()).hexdigest()[:8]
    callback_store[key] = {"tipo": "db", "formato": formato, "nombres": nombres}
    return key


def guardar_callback_externo(formato: str, lugares: list) -> str:
    """Guarda lugares externos (con coordenadas) y devuelve clave ≤8 chars."""
    nombres_clave = "|".join(l.get("nombre", "") for l in lugares)
    key = hashlib.md5(f"ext_{formato}{nombres_clave}".encode()).hexdigest()[:8]
    callback_store[key] = {"tipo": "externo", "formato": formato, "lugares": lugares}
    return key

# ──────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────

def detectar_lugares(texto: str) -> list:
    """Extrae todos los nombres de lugar de la respuesta del LLM usando múltiples patrones."""
    nombres = []
    seen = set()

    def agregar(name: str):
        name = re.sub(r"[.:,;!?]$", "", name).strip()
        if len(name) > 3 and name.lower() not in seen:
            seen.add(name.lower())
            nombres.append(name)

    # Patrón 1: **Nombre en negritas** (más confiable)
    for m in re.finditer(r"\*\*([A-ZÁÉÍÓÚÑ][^*\n]{2,60})\*\*", texto):
        agregar(m.group(1))
    if nombres:
        return nombres

    # Patrón 2: Lista numerada "1. Nombre" al inicio de línea
    for m in re.finditer(r"(?:^|\n)\d+[\.\)]\s+([A-ZÁÉÍÓÚÑ][^\n:]{3,60})", texto):
        agregar(m.group(1))
    if nombres:
        return nombres

    # Patrón 3: Lista con guión/bala "- Nombre" o "• Nombre"
    for m in re.finditer(r"(?:^|\n)[-•]\s+([A-ZÁÉÍÓÚÑ][^\n:]{3,60})", texto):
        agregar(m.group(1))
    if nombres:
        return nombres

    # Patrón 4: Nombre al inicio de línea con negritas opcionales (fallback)
    for m in re.finditer(r"(?:^|\n)\*{0,2}([A-ZÁÉÍÓÚÑ][^*\n]{3,50})\*{0,2}(?:\n|$)", texto):
        agregar(m.group(1))

    return nombres


def detectar_lugar(texto: str) -> str:
    """Extrae el primer nombre de lugar de la respuesta del LLM."""
    nombres = detectar_lugares(texto)
    return nombres[0] if nombres else None


def extraer_campo_texto(texto: str, campo: str) -> str:
    patron = rf"{campo}:\s*(.+)"
    match  = re.search(patron, texto)
    return match.group(1).strip() if match else ""


def buscar_datos_lugar(nombre: str) -> dict:
    """Busca datos completos de un lugar en ChromaDB por nombre."""
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        col    = client.get_or_create_collection("lugares_turisticos")

        resultado = col.get(where={"title": nombre})

        if not resultado["documents"]:
            todos = col.get(limit=200)
            for i, doc in enumerate(todos["documents"]):
                if nombre.lower() in doc.lower():
                    meta = todos["metadatas"][i]
                    return _meta_a_dict(meta, doc, nombre)
            return None

        meta = resultado["metadatas"][0]
        doc  = resultado["documents"][0]
        return _meta_a_dict(meta, doc, nombre)

    except Exception as e:
        logging.error(f"Error buscando datos de {nombre}: {e}")
        return None


def _meta_a_dict(meta: dict, doc: str, nombre: str) -> dict:
    return {
        "nombre":    meta.get("title", nombre),
        "thumbnail": meta.get("thumbnail", ""),
        "website":   meta.get("website", ""),
        "lat":       float(meta["lat"]) if meta.get("lat") else None,
        "lng":       float(meta["lng"]) if meta.get("lng") else None,
        "direccion": extraer_campo_texto(doc, "Dirección"),
        "telefono":  extraer_campo_texto(doc, "Teléfono"),
        "rating":    extraer_campo_texto(doc, "Calificación"),
        "horario":   extraer_campo_texto(doc, "Horario"),
        "categoria": extraer_campo_texto(doc, "Categoría de búsqueda"),
    }


TIPO_LABELS = {
    "restaurant": "Restaurante", "cafe": "Cafetería", "bar": "Bar",
    "pub": "Bar", "fast_food": "Comida rápida", "museum": "Museo",
    "hotel": "Hotel", "hostel": "Hostal", "guest_house": "Casa huésped",
    "attraction": "Atracción turística", "viewpoint": "Mirador",
    "gallery": "Galería de arte", "theatre": "Teatro", "cinema": "Cine",
    "pharmacy": "Farmacia", "bank": "Banco",
    "information": "Información turística", "monument": "Monumento",
    "ruins": "Ruinas", "castle": "Fortaleza", "church": "Iglesia",
    "place_of_worship": "Lugar de culto", "memorial": "Memorial",
}


async def mostrar_resultados_externos(update: Update, lat: float, lng: float):
    """Busca en OpenStreetMap (Overpass) cuando no hay datos locales."""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{API_URL}/buscar_externo",
                json={"lat": lat, "lng": lng, "radio_m": 1000},
                headers={"x-api-key": API_KEY}
            )

        if resp.status_code != 200:
            await update.message.reply_text(
                "🔍 La búsqueda externa no está disponible en este momento.\n"
                f"📍 Explora el área en Google Maps:\n"
                f"https://maps.google.com/?q={lat},{lng}"
            )
            return

        data     = resp.json()
        lugares  = data.get("lugares", [])

        if not lugares:
            await update.message.reply_text(
                "🔍 No encontré lugares registrados en un radio de 1 km.\n"
                f"📍 Explora la zona en Google Maps:\n"
                f"https://maps.google.com/?q={lat},{lng}"
            )
            return

        lineas = [
            "🔍 *Resultados de búsqueda en internet (OpenStreetMap):*\n",
            "_Estos resultados provienen de datos públicos de OpenStreetMap._\n"
        ]

        for i, lugar in enumerate(lugares[:8], 1):
            tipo   = TIPO_LABELS.get(lugar.get("tipo", ""), lugar.get("tipo", "Lugar"))
            dist   = lugar.get("distancia", 0)
            dist_t = f"{int(dist * 1000)} m" if dist < 1 else f"{dist:.1f} km"

            lineas.append(f"*{i}. {lugar['nombre']}* ({tipo}) — 🚶 {dist_t}")
            if lugar.get("direccion"):
                lineas.append(f"   📍 {lugar['direccion']}")
            if lugar.get("telefono"):
                lineas.append(f"   📞 {lugar['telefono']}")
            if lugar.get("horario"):
                lineas.append(f"   🕐 {lugar['horario']}")
            if lugar.get("website"):
                lineas.append(f"   🌐 {lugar['website']}")
            lineas.append("")

        await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

        teclado = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                f"🗺️ KML ({len(lugares)} lugares)",
                callback_data=f"map|{guardar_callback_externo('kml', lugares)}"
            ),
            InlineKeyboardButton(
                f"📍 GPX ({len(lugares)} lugares)",
                callback_data=f"map|{guardar_callback_externo('gpx', lugares)}"
            )
        ]])
        await update.message.reply_text(
            "¿Quieres descargar el mapa de estos lugares para navegar sin internet?",
            reply_markup=teclado
        )

    except httpx.TimeoutException:
        await update.message.reply_text(
            "⏳ La búsqueda externa tardó demasiado.\n"
            f"📍 Puedes explorar la zona en: https://maps.google.com/?q={lat},{lng}"
        )
    except Exception as e:
        logging.error(f"Error en búsqueda externa: {e}")
        await update.message.reply_text(
            "🔍 No pude completar la búsqueda externa.\n"
            f"📍 Explora el área en: https://maps.google.com/?q={lat},{lng}"
        )


async def keep_typing(chat_id: int, bot, stop_event: asyncio.Event):
    """Envía 'escribiendo...' cada 4 s mientras el LLM procesa la respuesta."""
    while not stop_event.is_set():
        await bot.send_chat_action(chat_id=chat_id, action="typing")
        await asyncio.sleep(4)


# ──────────────────────────────────────────────────────────
# HANDLERS DE TELEGRAM
# ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Compartir mi ubicación", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await update.message.reply_text(
        "🇨🇺 *Cuba Travel Guide*\n\n"
        "🇪🇸 Hola, soy tu guía turístico de Cuba. ¡Pregúntame en español!\n"
        "🇬🇧 Hi, I'm your Cuba travel guide. Ask me anything in English!\n"
        "🇮🇹 Ciao, sono la tua guida turistica di Cuba. Chiedimi in italiano!\n"
        "🇫🇷 Bonjour, je suis votre guide touristique de Cuba. Posez vos questions en français!\n"
        "🇩🇪 Hallo, ich bin dein Reiseführer für Kuba. Frag mich auf Deutsch!\n"
        "🇧🇷 Olá, sou seu guia turístico de Cuba. Pergunte em português!\n\n"
        "📍 Comparte tu ubicación para encontrar lugares cercanos\n"
        "❓ Escribe /ayuda para ver qué puedo hacer",
        parse_mode="Markdown",
        reply_markup=teclado
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra guía de uso del bot."""
    texto = (
        "🇨🇺 *Cuba Travel Guide — ¿Qué puedo hacer?*\n\n"
        "Puedes preguntarme en *cualquier idioma*:\n\n"
        "🍽️ *Gastronomía:*\n"
        "  \"¿Dónde comer en La Habana Vieja?\"\n"
        "  \"Best restaurants near Vedado\"\n\n"
        "🏛️ *Cultura e historia:*\n"
        "  \"¿Qué museos hay en La Habana?\"\n"
        "  \"Musei e monumenti all'Avana\"\n\n"
        "🌿 *Naturaleza:*\n"
        "  \"Parques naturales cerca del Vedado\"\n"
        "  \"Where can I see nature in Havana?\"\n\n"
        "🚌 *Transporte:*\n"
        "  \"¿Cómo llegar al aeropuerto?\"\n"
        "  \"Car rental in Havana\"\n\n"
        "📍 *Lugares cercanos:*\n"
        "  Comparte tu ubicación GPS → te muestro los 3 más cercanos\n"
        "  \"¿Qué hay cerca del Vedado?\"\n\n"
        "🗺️ *Mapas offline:*\n"
        "  Descarga KML o GPX para navegar sin internet en OsmAnd\n\n"
        "📋 *Comandos:*\n"
        "  /start — Reiniciar el bot\n"
        "  /ayuda — Esta ayuda\n"
        "  /reset — Borrar historial de conversación\n\n"
        "💡 El bot recuerda el contexto de la conversación. "
        "Puedes hacer preguntas de seguimiento como \"¿Y el horario?\" o \"Tell me more\""
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reinicia el historial de conversación del usuario."""
    usuario_id = str(update.message.from_user.id)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{API_URL}/reset",
                json={"usuario_id": usuario_id},
                headers={"x-api-key": API_KEY}
            )
    except Exception as e:
        logging.warning(f"No se pudo limpiar historial en API: {e}")

    context.user_data.clear()
    ultimos_lugares.pop(usuario_id, None)

    await update.message.reply_text(
        "🔄 Conversación reiniciada. ¡Hola de nuevo!\n"
        "¿En qué puedo ayudarte hoy? 🇨🇺"
    )


async def manejar_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe ubicación GPS compartida desde Telegram."""
    ubicacion  = update.message.location
    usuario_id = str(update.message.from_user.id)
    lat        = ubicacion.latitude
    lng        = ubicacion.longitude

    context.user_data["lat"] = lat
    context.user_data["lng"] = lng

    await update.message.reply_text("📡 Ubicación recibida. Buscando lugares cercanos...")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{API_URL}/cercanos",
                json={"lat": lat, "lng": lng, "usuario_id": usuario_id},
                headers={"x-api-key": API_KEY}
            )
            response.raise_for_status()
            data = response.json()

        lugares    = data.get("lugares", [])
        tiene_datos = data.get("tiene_datos", bool(lugares))

        if tiene_datos:
            await update.message.reply_text(data["respuesta"], parse_mode="Markdown")
            await enviar_tarjeta_lugar(update, lugares[0])
            nombres = [l["nombre"] for l in lugares]
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"🗺️ KML ({len(nombres)} lugares)",
                    callback_data=f"map|{guardar_callback('kml', nombres)}"
                )],
                [InlineKeyboardButton(
                    f"📍 GPX ({len(nombres)} lugares)",
                    callback_data=f"map|{guardar_callback('gpx', nombres)}"
                )]
            ])
            await update.message.reply_text(
                "¿Quieres el mapa para navegar sin internet?",
                reply_markup=teclado
            )
        else:
            await update.message.reply_text(
                "📭 No tengo datos de tu zona en mi base de datos.\n"
                "🔍 Buscando lugares cercanos en internet..."
            )
            await mostrar_resultados_externos(update, lat, lng)

    except httpx.ConnectError:
        await update.message.reply_text(
            "⚠️ No puedo conectarme al servidor. Asegúrate de que la API está corriendo."
        )
        logging.error("API no disponible en manejar_ubicacion")
    except Exception as e:
        await update.message.reply_text("Error buscando lugares cercanos. Intenta de nuevo.")
        logging.error(f"Error cercanos GPS: {e}")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal — detecta cercanía o responde con RAG + historial."""
    pregunta   = update.message.text
    usuario_id = str(update.message.from_user.id)

    logging.info(f">>> MENSAJE: '{pregunta}' de usuario {usuario_id}")

    palabras_cercania = [
        "cerca", "cercano", "próximo", "nearby", "close",
        "più vicino", "près", "in der nähe",
        "más cercano", "estoy en", "desde", "mi ubicación"
    ]
    es_cercania = any(p in pregunta.lower() for p in palabras_cercania)

    # Iniciar indicador de escritura persistente
    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(
        keep_typing(update.effective_chat.id, context.bot, stop_typing)
    )

    try:
        if es_cercania:
            lat = context.user_data.get("lat")
            lng = context.user_data.get("lng")

            payload = {"usuario_id": usuario_id}
            if lat and lng:
                payload["lat"] = lat
                payload["lng"] = lng
            else:
                payload["texto_ubicacion"] = pregunta

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{API_URL}/cercanos",
                    json=payload,
                    headers={"x-api-key": API_KEY}
                )
                response.raise_for_status()
                data = response.json()

            stop_typing.set()
            lugares     = data.get("lugares", [])
            tiene_datos = data.get("tiene_datos", bool(lugares))
            lat_ctx = context.user_data.get("lat")
            lng_ctx = context.user_data.get("lng")

            if tiene_datos:
                await update.message.reply_text(data["respuesta"], parse_mode="Markdown")
                await enviar_tarjeta_lugar(update, lugares[0])
                nombres = [l["nombre"] for l in lugares]
                teclado = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"🗺️ KML ({len(nombres)} lugares)",
                        callback_data=f"map|{guardar_callback('kml', nombres)}"
                    )],
                    [InlineKeyboardButton(
                        f"📍 GPX ({len(nombres)} lugares)",
                        callback_data=f"map|{guardar_callback('gpx', nombres)}"
                    )]
                ])
                await update.message.reply_text(
                    "¿Quieres el mapa para navegar sin internet?",
                    reply_markup=teclado
                )
            else:
                await update.message.reply_text(
                    "📭 No tengo datos de esa zona en mi base de datos.\n"
                    "🔍 Buscando en internet..."
                )
                if lat_ctx and lng_ctx:
                    await mostrar_resultados_externos(update, lat_ctx, lng_ctx)
                else:
                    await update.message.reply_text(
                        "Para buscar en internet comparte tu ubicación GPS "
                        "con el botón 📎 → Ubicación."
                    )

        else:
            # Flujo RAG con historial de conversación
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{API_URL}/chat",
                    json={"texto": pregunta, "usuario_id": usuario_id},
                    headers={"x-api-key": API_KEY}
                )
                response.raise_for_status()
                data = response.json()

            stop_typing.set()
            respuesta = data["respuesta"]

            nombres_lugares = detectar_lugares(respuesta)
            nombre_lugar    = nombres_lugares[0] if nombres_lugares else None
            lugar_datos     = None

            if nombre_lugar:
                ultimos_lugares[usuario_id] = nombre_lugar
                lugar_datos = buscar_datos_lugar(nombre_lugar)

            await update.message.reply_text(respuesta)

            if lugar_datos:
                # Tarjeta con imagen + botones KML/GPX para el primer lugar
                await enviar_tarjeta_lugar(update, lugar_datos)
                # Si hay más de un lugar mencionado, ofrecer mapa combinado
                if len(nombres_lugares) > 1:
                    lugares_con_datos = [
                        n for n in nombres_lugares if buscar_datos_lugar(n)
                    ]
                    if len(lugares_con_datos) > 1:
                        teclado = InlineKeyboardMarkup([[
                            InlineKeyboardButton(
                                f"🗺️ KML ({len(lugares_con_datos)} lugares)",
                                callback_data=f"map|{guardar_callback('kml', lugares_con_datos)}"
                            ),
                            InlineKeyboardButton(
                                f"📍 GPX ({len(lugares_con_datos)} lugares)",
                                callback_data=f"map|{guardar_callback('gpx', lugares_con_datos)}"
                            )
                        ]])
                        await update.message.reply_text(
                            f"🗺️ ¿Quieres un mapa con los *{len(lugares_con_datos)} lugares* mencionados?",
                            parse_mode="Markdown",
                            reply_markup=teclado
                        )

    except httpx.ConnectError:
        stop_typing.set()
        await update.message.reply_text(
            "⚠️ No puedo conectarme al servidor. ¿Está la API corriendo?\n"
            "Intenta de nuevo en unos momentos."
        )
        logging.error("API no disponible en responder")
    except httpx.TimeoutException:
        stop_typing.set()
        await update.message.reply_text(
            "⏳ La consulta tardó demasiado. Por favor intenta de nuevo."
        )
        logging.error("Timeout en responder")
    except httpx.HTTPStatusError as e:
        stop_typing.set()
        detalle = ""
        try:
            detalle = e.response.json().get("detail", "")
        except Exception:
            pass
        logging.error(f"Error API {e.response.status_code}: {detalle}")
        await update.message.reply_text(
            "Lo siento, ocurrió un error en el servidor. Por favor intenta de nuevo."
        )
    except Exception as e:
        stop_typing.set()
        await update.message.reply_text(
            "Lo siento, ocurrió un error inesperado. Por favor intenta de nuevo."
        )
        logging.error(f"Error en responder: {e}")
    finally:
        stop_typing.set()
        typing_task.cancel()


async def enviar_tarjeta_lugar(update: Update, lugar: dict):
    """Envía imagen + caption + botones web y mapa."""
    nombre    = lugar.get("nombre", "")
    thumbnail = lugar.get("thumbnail", "")
    categoria = lugar.get("categoria", "")
    website   = lugar.get("website", "")

    imagen_url = await obtener_imagen(thumbnail, nombre, categoria)
    caption    = construir_caption(lugar)

    botones = []
    if website:
        botones.append([InlineKeyboardButton("🌐 Sitio web oficial", url=website)])
    botones.append([
        InlineKeyboardButton("🗺️ KML", callback_data=f"map|{guardar_callback('kml', [nombre])}"),
        InlineKeyboardButton("📍 GPX", callback_data=f"map|{guardar_callback('gpx', [nombre])}")
    ])

    teclado = InlineKeyboardMarkup(botones)

    try:
        await update.message.reply_photo(
            photo=imagen_url,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=teclado
        )
    except Exception:
        # Fallback sin imagen
        await update.message.reply_text(
            caption,
            parse_mode="Markdown",
            reply_markup=teclado
        )


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja todos los botones inline — usa callback_store para evitar límite de 64 bytes."""
    query      = update.callback_query
    await query.answer()

    usuario_id = str(query.from_user.id)
    datos      = query.data.split("|", 1)

    # Formato: "map|<clave>"
    if datos[0] == "map" and len(datos) > 1:
        stored = callback_store.get(datos[1], {})
        formato_real = stored.get("formato", "kml")
        tipo_callback = stored.get("tipo", "db")
    else:
        # Compatibilidad con botones anteriores
        formato_real  = "kml" if "kml" in datos[0] else "gpx"
        tipo_callback = "db"
        stored        = {"nombres": [datos[1]] if len(datos) > 1 else [ultimos_lugares.get(usuario_id, "")]}

    instrucciones = (
        "📱 *Cómo usar en OsmAnd:*\n"
        "1. Descarga el archivo\n"
        "2. Abre OsmAnd\n"
        "3. Menú → Mis lugares → Importar\n"
        "4. Selecciona el archivo\n"
        "5. ¡Navega sin internet! 🗺️"
    )

    try:
        if tipo_callback == "externo":
            lugares_ext = stored.get("lugares", [])
            if not lugares_ext:
                await query.message.reply_text("No hay datos para generar el mapa.")
                return

            label = f"{len(lugares_ext)} lugares"
            await query.message.reply_text(
                f"⏳ Generando {formato_real.upper()} para *{label}*...",
                parse_mode="Markdown"
            )

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{API_URL}/mapa/{formato_real}_externo",
                    json={"lugares": lugares_ext},
                    headers={"x-api-key": API_KEY}
                )

            if resp.status_code == 200:
                ruta_temp = f"lugares_externos.{formato_real}"
                with open(ruta_temp, "wb") as f:
                    f.write(resp.content)
                with open(ruta_temp, "rb") as f:
                    await query.message.reply_document(
                        document=f,
                        filename=f"lugares_cercanos.{formato_real}",
                        caption=instrucciones,
                        parse_mode="Markdown"
                    )
                os.remove(ruta_temp)
            else:
                await query.message.reply_text("Error generando el mapa externo. Intenta de nuevo.")

        else:
            # Flujo DB: buscar por nombre en ChromaDB
            nombres = stored.get("nombres", [])
            nombres = [n.strip() for n in nombres if n.strip()]

            if not nombres:
                await query.message.reply_text("No pude identificar el lugar. Pregunta de nuevo.")
                return

            label = nombres[0] if len(nombres) == 1 else f"{len(nombres)} lugares"
            await query.message.reply_text(
                f"⏳ Generando {formato_real.upper()} para *{label}*...",
                parse_mode="Markdown"
            )

            response_ok    = None
            nombre_exitoso = None
            async with httpx.AsyncClient(timeout=30) as client:
                for nombre_candidato in nombres:
                    resp = await client.post(
                        f"{API_URL}/mapa/{formato_real}",
                        json={"place_id": "", "nombre": nombre_candidato},
                        headers={"x-api-key": API_KEY}
                    )
                    if resp.status_code == 200:
                        response_ok    = resp
                        nombre_exitoso = nombre_candidato
                        break

            if response_ok:
                nombre_arch = nombre_exitoso.replace(" ", "_")[:30]
                ruta_temp   = f"{nombre_arch}.{formato_real}"
                with open(ruta_temp, "wb") as f:
                    f.write(response_ok.content)
                with open(ruta_temp, "rb") as f:
                    await query.message.reply_document(
                        document=f,
                        filename=f"{nombre_arch}.{formato_real}",
                        caption=instrucciones,
                        parse_mode="Markdown"
                    )
                os.remove(ruta_temp)
            else:
                await query.message.reply_text(
                    f"No encontré coordenadas GPS para *{label}*.\n"
                    "Este lugar puede no tener datos de ubicación en nuestra base de datos.",
                    parse_mode="Markdown"
                )

    except Exception as e:
        await query.message.reply_text("Error generando el archivo. Intenta de nuevo.")
        logging.error(f"Error mapa {formato_real}: {e}")


# ──────────────────────────────────────────────────────────
# INICIO
# ──────────────────────────────────────────────────────────

def main():
    from telegram.request import HTTPXRequest
    builder = Application.builder().token(TOKEN)
    if PROXY_URL:
        request = HTTPXRequest(proxy=PROXY_URL)
        builder = builder.request(request)
    app = builder.build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("help",  ayuda))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.LOCATION, manejar_ubicacion))
    app.add_handler(CallbackQueryHandler(manejar_botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot corriendo... Ctrl+C para detener")
    app.run_polling()


if __name__ == "__main__":
    main()
