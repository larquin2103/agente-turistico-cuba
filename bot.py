import logging
import re
import requests
import os
# Proxy para Telegram (red corporativa)
PROXY_URL = "http://10.11.0.9:8080"

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

# ─────────────────────────────────────────────
# CONFIGURACIÓN — edita solo estas líneas
# ─────────────────────────────────────────────
TOKEN   = "8177591854:AAHuTtU-G7kWYZqOZwzDduXYWiNax2Xswns"   # ← reemplaza esto
API_URL = "http://localhost:8000"
API_KEY = "turismo-secret-2024"
DB_PATH = "C:/Users/larquin/agente-turistico/db"
# ─────────────────────────────────────────────

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
            # Búsqueda parcial en texto
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
        "🇨🇺 Cuba Travel Guide\n\n"
        "🇪🇸 Hola, soy tu guía turístico de Cuba. ¡Pregúntame en español!\n"
        "🇬🇧 Hi, I'm your Cuba travel guide. Ask me anything in English!\n"
        "🇮🇹 Ciao, sono la tua guida turistica di Cuba. Chiedimi in italiano!\n"
        "🇫🇷 Bonjour, je suis votre guide touristique de Cuba. Posez vos questions en français!\n"
        "🇩🇪 Hallo, ich bin dein Reiseführer für Kuba. Frag mich auf Deutsch!\n"
        "🇧🇷 Olá, sou seu guia turístico de Cuba. Pergunte em português!\n\n"
        "📍 Share your location to find nearby places",
        reply_markup=teclado
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
        response = requests.post(
            f"{API_URL}/cercanos",
            json={"lat": lat, "lng": lng, "usuario_id": usuario_id},
            headers={"x-api-key": API_KEY},
            timeout=30
        )
        data    = response.json()
        lugares = data.get("lugares", [])

        await update.message.reply_text(data["respuesta"], parse_mode="Markdown")

        if lugares:
            # Mostrar imagen del lugar más cercano
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

    except Exception as e:
        await update.message.reply_text("Error buscando lugares cercanos.")
        logging.error(f"Error cercanos GPS: {e}")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal — detecta cercanía o responde con RAG."""
    pregunta   = update.message.text
    usuario_id = str(update.message.from_user.id)

    print(f">>> MENSAJE RECIBIDO: '{pregunta}' de usuario {usuario_id}")
    logging.info(f">>> LLAMANDO API con: {pregunta}")

    palabras_cercania = [
        "cerca", "cercano", "próximo", "nearby", "close",
        "più vicino", "près", "in der nähe",
        "más cercano", "estoy en", "desde", "mi ubicación"
    ]
    es_cercania = any(p in pregunta.lower() for p in palabras_cercania)

    await update.message.chat.send_action("typing")

    if es_cercania:
        lat = context.user_data.get("lat")
        lng = context.user_data.get("lng")

        payload = {"usuario_id": usuario_id}
        if lat and lng:
            payload["lat"] = lat
            payload["lng"] = lng
        else:
            payload["texto_ubicacion"] = pregunta

        try:
            response = requests.post(
                f"{API_URL}/cercanos",
                json=payload,
                headers={"x-api-key": API_KEY},
                timeout=30
            )
            data    = response.json()
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
        except Exception as e:
            await update.message.reply_text("Error buscando lugares cercanos.")
            logging.error(f"Error cercanos texto: {e}")

    else:
        # Flujo RAG normal
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"texto": pregunta, "usuario_id": usuario_id},
                headers={"x-api-key": API_KEY},
                timeout=120
            )
            data      = response.json()
            respuesta = data["respuesta"]

            nombre_lugar = detectar_lugar(respuesta)
            lugar_datos  = None

            if nombre_lugar:
                ultimos_lugares[usuario_id] = nombre_lugar
                lugar_datos = buscar_datos_lugar(nombre_lugar)

            await update.message.reply_text(respuesta)

            if lugar_datos:
                await enviar_tarjeta_lugar(update, lugar_datos)

        except Exception as e:
            await update.message.reply_text("Error. Intenta de nuevo.")
            logging.error(f"Error RAG: {e}")


async def enviar_tarjeta_lugar(update: Update, lugar: dict):
    """Envía imagen + caption + botones web y mapa."""
    nombre    = lugar.get("nombre", "")
    thumbnail = lugar.get("thumbnail", "")
    categoria = lugar.get("categoria", "")
    website   = lugar.get("website", "")

    imagen_url = obtener_imagen(thumbnail, nombre, categoria)
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

    # Determinar formato real y nombres
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
        # Generar un archivo por cada nombre y enviar el primero (o combinar)
        nombre_principal = nombres[0]
        response = requests.post(
            f"{API_URL}/mapa/{formato_real}",
            json={"place_id": "", "nombre": nombre_principal},
            headers={"x-api-key": API_KEY},
            timeout=30
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
    request = HTTPXRequest(proxy=PROXY_URL)
    app = Application.builder().token(TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, manejar_ubicacion))
    app.add_handler(CallbackQueryHandler(manejar_botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("Bot corriendo... Ctrl+C para detener")
    app.run_polling()


if __name__ == "__main__":
    main()