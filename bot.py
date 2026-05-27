import logging
import re
import os
import asyncio
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

# ──────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────

def detectar_lugar(texto: str) -> str:
    """Extrae el primer nombre de lugar en negritas de la respuesta RAG."""
    match = re.search(r"(?:^|\n)\*{0,2}([A-ZÁÉÍÓÚÑ][^*\n]{3,50})\*{0,2}(?:\n|$)", texto)
    return match.group(1).strip() if match else None


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

        lugares = data.get("lugares", [])
        await update.message.reply_text(data["respuesta"], parse_mode="Markdown")

        if lugares:
            await enviar_tarjeta_lugar(update, lugares[0])

            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🗺️ Mapa KML con los 3 lugares",
                    callback_data=f"kml_multi|{','.join([l['nombre'] for l in lugares])}"
                )],
                [InlineKeyboardButton(
                    "📍 Mapa GPX con los 3 lugares",
                    callback_data=f"gpx_multi|{','.join([l['nombre'] for l in lugares])}"
                )]
            ])
            await update.message.reply_text(
                "¿Quieres el mapa para navegar sin internet?",
                reply_markup=teclado
            )

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
            lugares = data.get("lugares", [])
            await update.message.reply_text(data["respuesta"], parse_mode="Markdown")

            if lugares:
                await enviar_tarjeta_lugar(update, lugares[0])
                teclado = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "🗺️ Mapa KML",
                        callback_data=f"kml_multi|{','.join([l['nombre'] for l in lugares])}"
                    )],
                    [InlineKeyboardButton(
                        "📍 Mapa GPX",
                        callback_data=f"gpx_multi|{','.join([l['nombre'] for l in lugares])}"
                    )]
                ])
                await update.message.reply_text(
                    "¿Quieres el mapa para navegar sin internet?",
                    reply_markup=teclado
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

            nombre_lugar = detectar_lugar(respuesta)
            lugar_datos  = None

            if nombre_lugar:
                ultimos_lugares[usuario_id] = nombre_lugar
                lugar_datos = buscar_datos_lugar(nombre_lugar)

            await update.message.reply_text(respuesta)

            if lugar_datos:
                await enviar_tarjeta_lugar(update, lugar_datos)

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
            "⏳ La consulta tardó demasiado. El modelo LLM puede estar ocupado.\n"
            "Por favor intenta de nuevo."
        )
        logging.error("Timeout en responder")
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
        InlineKeyboardButton("🗺️ KML", callback_data=f"kml|{nombre}"),
        InlineKeyboardButton("📍 GPX", callback_data=f"gpx|{nombre}")
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
    """Maneja todos los botones inline — KML, GPX, kml_multi, gpx_multi."""
    query      = update.callback_query
    await query.answer()

    usuario_id = str(query.from_user.id)
    datos      = query.data.split("|", 1)
    formato    = datos[0]   # kml / gpx / kml_multi / gpx_multi
    contenido  = datos[1] if len(datos) > 1 else ""

    es_multi      = "multi" in formato
    formato_real  = "kml" if "kml" in formato else "gpx"
    nombres       = contenido.split(",") if es_multi else [contenido or ultimos_lugares.get(usuario_id, "")]
    nombres       = [n.strip() for n in nombres if n.strip()]

    if not nombres:
        await query.message.reply_text("No pude identificar el lugar. Pregunta de nuevo.")
        return

    label = nombres[0] if len(nombres) == 1 else f"{len(nombres)} lugares"
    await query.message.reply_text(
        f"⏳ Generando {formato_real.upper()} para *{label}*...",
        parse_mode="Markdown"
    )

    try:
        nombre_principal = nombres[0]
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{API_URL}/mapa/{formato_real}",
                json={"place_id": "", "nombre": nombre_principal},
                headers={"x-api-key": API_KEY}
            )

        if response.status_code == 200:
            nombre_arch = nombre_principal.replace(" ", "_")[:30]
            ruta_temp   = f"{nombre_arch}.{formato_real}"

            with open(ruta_temp, "wb") as f:
                f.write(response.content)

            instrucciones = (
                "📱 *Cómo usar en OsmAnd:*\n"
                "1. Descarga el archivo\n"
                "2. Abre OsmAnd\n"
                "3. Menú → Mis lugares → Importar\n"
                "4. Selecciona el archivo\n"
                "5. ¡Navega sin internet! 🗺️"
            )

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
                f"No encontré coordenadas GPS para *{nombre_principal}*.",
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
