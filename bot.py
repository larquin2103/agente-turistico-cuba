import logging
import re
import io
import os
import asyncio
import hashlib
import time
import httpx
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURACIÓN — leída desde .env
# ─────────────────────────────────────────────
PROXY_URL = os.getenv("PROXY_URL", "")
TOKEN     = os.getenv("TELEGRAM_TOKEN")
API_URL   = os.getenv("API_URL", "http://localhost:8000")
API_KEY   = os.getenv("API_KEY")
# ─────────────────────────────────────────────

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from media import obtener_imagen, construir_caption

logging.basicConfig(level=logging.INFO)

# Último lugar mencionado por usuario
ultimos_lugares: dict = {}

# Almacén de callbacks con TTL — evita superar el límite de 64 bytes de Telegram
callback_store: dict = {}

# Rate limiting — {user_id: [timestamps]}
_rate_limit: dict = defaultdict(list)

# Máximo de tarjetas visuales por respuesta
MAX_TARJETAS = 3

# Palabra clave detectada en el texto del usuario → filtro de "Categoría de búsqueda"
CATEGORIA_FILTROS = {
    "restaurante": "gastronomia", "restaurant": "gastronomia", "ristorante": "gastronomia",
    "comida": "gastronomia", "food": "gastronomia", "essen": "gastronomia",
    "gastronomia": "gastronomia", "gastronomía": "gastronomia", "comer": "gastronomia",
    "museo": "tradi", "museum": "tradi", "musée": "tradi", "museu": "tradi",
    "cultura": "tradi", "culture": "tradi", "cultural": "tradi", "kultur": "tradi",
    "naturaleza": "natural", "nature": "natural", "natur": "natural",
    "parque": "natural", "park": "natural",
    "transporte": "transpor", "transport": "transpor",
    "auto": "transpor", "car": "transpor", "rentar": "transpor", "alquiler": "transpor",
    "hotel": "servicio", "alojamiento": "servicio", "accommodation": "servicio",
}


def detectar_categoria(texto: str) -> str:
    """Detecta un filtro de categoría a partir de palabras clave en el texto del usuario."""
    texto_lower = texto.lower()
    for palabra, filtro in CATEGORIA_FILTROS.items():
        if palabra in texto_lower:
            return filtro
    return None


def _check_rate_limit(user_id: str, max_req: int = 5, ventana_seg: int = 60) -> bool:
    """True si el usuario puede continuar, False si excedió el límite."""
    ahora = time.time()
    _rate_limit[user_id] = [t for t in _rate_limit[user_id] if ahora - t < ventana_seg]
    if len(_rate_limit[user_id]) >= max_req:
        return False
    _rate_limit[user_id].append(ahora)
    return True


def _limpiar_callback_store(ttl_horas: int = 24):
    """Elimina entradas con más de ttl_horas de antigüedad."""
    ahora     = time.time()
    expirados = [k for k, v in list(callback_store.items())
                 if ahora - v.get("_ts", 0) > ttl_horas * 3600]
    for k in expirados:
        del callback_store[k]


def guardar_callback(formato: str, nombres: list) -> str:
    """Guarda nombres de lugares de BD y devuelve clave ≤8 chars para callback_data."""
    key = hashlib.md5(f"{formato}{'|'.join(nombres)}".encode()).hexdigest()[:8]
    callback_store[key] = {
        "tipo": "db", "formato": formato,
        "nombres": nombres, "_ts": time.time()
    }
    _limpiar_callback_store()
    return key


def guardar_callback_externo(formato: str, lugares: list) -> str:
    """Guarda lugares externos (con coordenadas) y devuelve clave ≤8 chars."""
    nombres_clave = "|".join(l.get("nombre", "") for l in lugares)
    key = hashlib.md5(f"ext_{formato}{nombres_clave}".encode()).hexdigest()[:8]
    callback_store[key] = {
        "tipo": "externo", "formato": formato,
        "lugares": lugares, "_ts": time.time()
    }
    _limpiar_callback_store()
    return key


# ──────────────────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────────────────

def detectar_lugares(texto: str) -> list:
    """Extrae todos los nombres de lugar de la respuesta del LLM."""
    nombres = []
    seen    = set()

    def agregar(name: str):
        name = re.sub(r"[.:,;!?]$", "", name).strip()
        if len(name) > 3 and name.lower() not in seen:
            seen.add(name.lower())
            nombres.append(name)

    for m in re.finditer(r"\*\*([A-ZÁÉÍÓÚÑ][^*\n]{2,60})\*\*", texto):
        agregar(m.group(1))
    if nombres:
        return nombres

    for m in re.finditer(r"(?:^|\n)\d+[\.\)]\s+([A-ZÁÉÍÓÚÑ][^\n:]{3,60})", texto):
        agregar(m.group(1))
    if nombres:
        return nombres

    for m in re.finditer(r"(?:^|\n)[-•]\s+([A-ZÁÉÍÓÚÑ][^\n:]{3,60})", texto):
        agregar(m.group(1))
    if nombres:
        return nombres

    for m in re.finditer(r"(?:^|\n)\*{0,2}([A-ZÁÉÍÓÚÑ][^*\n]{3,50})\*{0,2}(?:\n|$)", texto):
        agregar(m.group(1))

    return nombres


def detectar_lugar(texto: str) -> str:
    nombres = detectar_lugares(texto)
    return nombres[0] if nombres else None


async def buscar_datos_lugar(nombre: str) -> dict:
    """Busca datos de un lugar via API (exact → fuzzy → vectorial)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{API_URL}/buscar_lugar",
                json={"nombre": nombre},
                headers={"x-api-key": API_KEY}
            )
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        logging.error(f"Error buscando datos de {nombre}: {e}")
        return None


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


async def mostrar_resultados_externos(update: Update, lat: float, lng: float, radio_m: int = 1000):
    """Busca en OpenStreetMap (Overpass) cuando no hay datos locales."""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{API_URL}/buscar_externo",
                json={"lat": lat, "lng": lng, "radio_m": radio_m},
                headers={"x-api-key": API_KEY}
            )

        if resp.status_code != 200:
            await update.message.reply_text(
                "🔍 La búsqueda externa no está disponible en este momento.\n"
                f"📍 Explora el área en Google Maps:\nhttps://maps.google.com/?q={lat},{lng}"
            )
            return

        data    = resp.json()
        lugares = data.get("lugares", [])

        if not lugares:
            radio_km = radio_m / 1000
            mensaje = (
                f"🔍 No encontré lugares en un radio de {radio_km:.0f} km.\n"
                f"📍 Explora la zona en Google Maps:\nhttps://maps.google.com/?q={lat},{lng}"
            )
            if radio_m < 3000:
                teclado = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔍 Ampliar búsqueda a 3 km", callback_data=f"ampliar|{lat}|{lng}")
                ]])
                await update.message.reply_text(mensaje, reply_markup=teclado)
            else:
                await update.message.reply_text(mensaje)
            return

        lineas = [
            "🔍 *Resultados de búsqueda en internet (OpenStreetMap):*\n",
            "_Datos públicos de OpenStreetMap._\n"
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
            if lugar.get("lat") and lugar.get("lng"):
                lineas.append(
                    f"   [Ver en Google Maps](https://maps.google.com/?q={lugar['lat']},{lugar['lng']})"
                )
            lineas.append("")

        await update.message.reply_text(
            "\n".join(lineas),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

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
            "¿Quieres descargar el mapa para navegar sin internet?",
            reply_markup=teclado
        )

    except httpx.TimeoutException:
        await update.message.reply_text(
            "⏳ La búsqueda externa tardó demasiado.\n"
            f"📍 Explora la zona en: https://maps.google.com/?q={lat},{lng}"
        )
    except Exception as e:
        logging.error(f"Error en búsqueda externa: {e}")
        await update.message.reply_text(
            "🔍 No pude completar la búsqueda externa.\n"
            f"📍 Explora el área en: https://maps.google.com/?q={lat},{lng}"
        )


async def keep_typing(chat_id: int, bot, stop_event: asyncio.Event):
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
        "❓ /ayuda — qué puedo hacer\n"
        "🆘 /emergencia — números de urgencia en Cuba",
        parse_mode="Markdown",
        reply_markup=teclado
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "  Comparte tu ubicación GPS → los más cercanos\n"
        "  \"¿Qué hay cerca del Vedado?\"\n\n"
        "🗺️ *Mapas offline (OsmAnd / Maps.me):*\n"
        "  Descarga KML o GPX para navegar sin internet\n\n"
        "🎙️ *Notas de voz:*\n"
        "  Envía un audio con tu pregunta, te entiendo igual\n\n"
        "📋 *Comandos:*\n"
        "  /start — Reiniciar\n"
        "  /ayuda — Esta ayuda\n"
        "  /reset — Borrar historial de conversación\n"
        "  /emergencia — Números de urgencia en Cuba\n\n"
        "💡 El bot recuerda el contexto. Puedes preguntar "
        "\"¿Y el horario?\" o \"Tell me more\" como seguimiento."
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def emergencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Números de emergencia y contactos útiles en Cuba."""
    await update.message.reply_text(
        "🆘 *Emergencias en Cuba*\n\n"
        "🚒 Bomberos: *105*\n"
        "🚓 Policía: *106*\n"
        "🚑 Ambulancia / Urgencias: *104*\n"
        "⚡ Avería eléctrica: *185*\n\n"
        "🏥 *Hospitales para extranjeros — La Habana:*\n\n"
        "• *Cira García* (CIMEX)\n"
        "  📍 Calle 20 No. 4101 esq. 41, Miramar\n"
        "  📞 +53 7 204-2811\n\n"
        "• *Hermanos Ameijeiras*\n"
        "  📍 San Lázaro 701, Centro Habana\n"
        "  📞 +53 7 876-1000\n\n"
        "💱 *Casas de cambio (CADECA):*\n"
        "  • Obispo y Cuba, La Habana Vieja\n"
        "  • Hotel Nacional, Vedado\n"
        "  • Aeropuerto José Martí\n\n"
        "📞 *Asisttur* (asistencia al turista):\n"
        "  +53 7 866-4499 | asisttur.cu",
        parse_mode="Markdown"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        lugares     = data.get("lugares", [])
        tiene_datos = data.get("tiene_datos", bool(lugares))

        if tiene_datos:
            await update.message.reply_text(data["respuesta"], parse_mode="Markdown")
            for lugar in lugares[:MAX_TARJETAS]:
                await enviar_tarjeta_lugar(update, lugar)
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
    """Handler principal — valida rate limit y delega a procesar_pregunta()."""
    pregunta   = update.message.text
    usuario_id = str(update.message.from_user.id)

    if not _check_rate_limit(usuario_id):
        await update.message.reply_text(
            "⏱️ Demasiadas consultas seguidas. Espera un momento e intenta de nuevo."
        )
        return

    await procesar_pregunta(update, context, pregunta, usuario_id)


async def procesar_pregunta(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             pregunta: str, usuario_id: str):
    """Detecta cercanía o responde con RAG + historial."""
    logging.info(f">>> MENSAJE: '{pregunta}' de usuario {usuario_id}")

    palabras_cercania = [
        "cerca", "cercano", "próximo", "nearby", "close to", "close by",
        "più vicino", "près", "in der nähe", "perto",
        "más cercano", "estoy en", "mi ubicación"
    ]
    es_cercania = any(p in pregunta.lower() for p in palabras_cercania)

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

            categoria = detectar_categoria(pregunta)
            if categoria:
                payload["categoria"] = categoria

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
            lat_ctx     = context.user_data.get("lat")
            lng_ctx     = context.user_data.get("lng")

            if tiene_datos:
                await update.message.reply_text(data["respuesta"], parse_mode="Markdown")
                for lugar in lugares[:MAX_TARJETAS]:
                    await enviar_tarjeta_lugar(update, lugar)
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
            # ── Flujo RAG con historial ──
            payload = {"texto": pregunta, "usuario_id": usuario_id}
            lat_ctx = context.user_data.get("lat")
            lng_ctx = context.user_data.get("lng")
            if lat_ctx and lng_ctx:
                payload["lat"] = lat_ctx
                payload["lng"] = lng_ctx

            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{API_URL}/chat",
                    json=payload,
                    headers={"x-api-key": API_KEY}
                )
                response.raise_for_status()
                data = response.json()

            stop_typing.set()
            respuesta_texto = data["respuesta"]
            nombres_lugares = detectar_lugares(respuesta_texto)

            await update.message.reply_text(respuesta_texto)

            if nombres_lugares:
                ultimos_lugares[usuario_id] = nombres_lugares[0]

                lugares_con_db = []

                for nombre_candidato in nombres_lugares[:MAX_TARJETAS * 2]:
                    datos = await buscar_datos_lugar(nombre_candidato)
                    if datos and datos.get("lat"):
                        lugares_con_db.append(datos)
                        await enviar_tarjeta_lugar(update, datos)
                        if len(lugares_con_db) >= MAX_TARJETAS:
                            break

                if len(lugares_con_db) > 1:
                    nombres_mapa = [l["nombre"] for l in lugares_con_db]
                    teclado = InlineKeyboardMarkup([[
                        InlineKeyboardButton(
                            f"🗺️ KML ({len(nombres_mapa)} lugares)",
                            callback_data=f"map|{guardar_callback('kml', nombres_mapa)}"
                        ),
                        InlineKeyboardButton(
                            f"📍 GPX ({len(nombres_mapa)} lugares)",
                            callback_data=f"map|{guardar_callback('gpx', nombres_mapa)}"
                        )
                    ]])
                    await update.message.reply_text(
                        f"🗺️ ¿Quieres un mapa con los *{len(nombres_mapa)} lugares* mencionados?",
                        parse_mode="Markdown",
                        reply_markup=teclado
                    )

    except httpx.ConnectError:
        stop_typing.set()
        await update.message.reply_text(
            "⚠️ No puedo conectarme al servidor. ¿Está la API corriendo?\n"
            "Intenta de nuevo en unos momentos."
        )
        logging.error("API no disponible en procesar_pregunta")
    except httpx.TimeoutException:
        stop_typing.set()
        await update.message.reply_text(
            "⏳ La consulta tardó demasiado. Por favor intenta de nuevo."
        )
        logging.error("Timeout en procesar_pregunta")
    except httpx.HTTPStatusError as e:
        stop_typing.set()
        detalle = ""
        try:
            detalle = e.response.json().get("detail", "")
        except Exception:
            pass
        logging.error(f"Error API {e.response.status_code}: {detalle}")
        if e.response.status_code == 429:
            await update.message.reply_text(
                detalle or "⏱️ Hemos alcanzado el límite de consultas. Espera un momento e intenta de nuevo."
            )
        else:
            await update.message.reply_text(
                "Lo siento, ocurrió un error en el servidor. Por favor intenta de nuevo."
            )
    except Exception as e:
        stop_typing.set()
        await update.message.reply_text(
            "Lo siento, ocurrió un error inesperado. Por favor intenta de nuevo."
        )
        logging.error(f"Error en procesar_pregunta: {e}")
    finally:
        stop_typing.set()
        typing_task.cancel()


async def manejar_voz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transcribe notas de voz con Groq Whisper y las procesa como texto (F5)."""
    usuario_id = str(update.message.from_user.id)

    if not _check_rate_limit(usuario_id):
        await update.message.reply_text(
            "⏱️ Demasiadas consultas seguidas. Espera un momento e intenta de nuevo."
        )
        return

    await update.message.reply_text("🎙️ Transcribiendo audio...")

    try:
        voz         = update.message.voice or update.message.audio
        archivo     = await voz.get_file()
        audio_bytes = bytes(await archivo.download_as_bytearray())

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{API_URL}/transcribir",
                files={"audio": ("audio.ogg", audio_bytes, "audio/ogg")},
                headers={"x-api-key": API_KEY}
            )
            resp.raise_for_status()
            texto = resp.json().get("texto", "").strip()

        if not texto:
            await update.message.reply_text(
                "No pude entender el audio. Intenta de nuevo o escribe tu pregunta."
            )
            return

        await update.message.reply_text(f"🎙️ _Escuché:_ \"{texto}\"", parse_mode="Markdown")
        await procesar_pregunta(update, context, texto, usuario_id)

    except httpx.ConnectError:
        await update.message.reply_text(
            "⚠️ No puedo conectarme al servidor. Asegúrate de que la API está corriendo."
        )
        logging.error("API no disponible en manejar_voz")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            await update.message.reply_text(
                "⏱️ Hemos alcanzado el límite de transcripciones. Intenta de nuevo en unos momentos."
            )
        else:
            await update.message.reply_text("No pude procesar el audio. Intenta de nuevo.")
        logging.error(f"Error transcribiendo voz: {e}")
    except Exception as e:
        await update.message.reply_text("No pude procesar el audio. Intenta de nuevo.")
        logging.error(f"Error transcribiendo voz: {e}")


async def enviar_tarjeta_lugar(update: Update, lugar: dict):
    """Envía imagen + caption + botones: web, Google Maps y mapas offline."""
    nombre    = lugar.get("nombre", "")
    thumbnail = lugar.get("thumbnail", "")
    categoria = lugar.get("categoria", "")
    website   = lugar.get("website", "")
    lat       = lugar.get("lat")
    lng       = lugar.get("lng")

    imagen_url = await obtener_imagen(thumbnail, nombre, categoria)
    caption    = construir_caption(lugar)

    botones = []
    if website:
        botones.append([InlineKeyboardButton("🌐 Sitio web oficial", url=website)])
    if lat and lng:
        gmaps_url = f"https://maps.google.com/?q={lat},{lng}"
        botones.append([InlineKeyboardButton("📍 Ver en Google Maps", url=gmaps_url)])
    botones.append([
        InlineKeyboardButton("🗺️ KML offline", callback_data=f"map|{guardar_callback('kml', [nombre])}"),
        InlineKeyboardButton("📍 GPX offline", callback_data=f"map|{guardar_callback('gpx', [nombre])}")
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
        await update.message.reply_text(
            caption,
            parse_mode="Markdown",
            reply_markup=teclado
        )


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja botones inline — usa callback_store para evitar límite de 64 bytes."""
    query      = update.callback_query
    await query.answer()

    usuario_id = str(query.from_user.id)
    datos      = query.data.split("|")

    if datos[0] == "ampliar" and len(datos) >= 3:
        lat, lng = float(datos[1]), float(datos[2])
        await query.message.reply_text("🔍 Ampliando búsqueda a 3 km...")
        await mostrar_resultados_externos(update, lat, lng, radio_m=3000)
        return

    if datos[0] == "map" and len(datos) > 1:
        stored        = callback_store.get(datos[1], {})
        formato_real  = stored.get("formato", "kml")
        tipo_callback = stored.get("tipo", "db")
    else:
        formato_real  = "kml" if "kml" in datos[0] else "gpx"
        tipo_callback = "db"
        stored        = {"nombres": [datos[1]] if len(datos) > 1 else [ultimos_lugares.get(usuario_id, "")]}

    instrucciones = (
        "📱 *Cómo usar en OsmAnd / Maps.me:*\n"
        "1. Descarga el archivo\n"
        "2. Abre OsmAnd o Maps.me\n"
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
                buf      = io.BytesIO(resp.content)
                buf.name = f"lugares_cercanos.{formato_real}"
                await query.message.reply_document(
                    document=buf,
                    filename=f"lugares_cercanos.{formato_real}",
                    caption=instrucciones,
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text("Error generando el mapa externo. Intenta de nuevo.")

        else:
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

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{API_URL}/mapa/{formato_real}_multi",
                    json={"nombres": nombres},
                    headers={"x-api-key": API_KEY}
                )

            if resp.status_code == 200:
                nombre_arch = (
                    nombres[0].replace(" ", "_")[:30] if len(nombres) == 1
                    else "lugares_turisticos"
                )
                buf      = io.BytesIO(resp.content)
                buf.name = f"{nombre_arch}.{formato_real}"
                await query.message.reply_document(
                    document=buf,
                    filename=f"{nombre_arch}.{formato_real}",
                    caption=instrucciones,
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text(
                    f"No encontré coordenadas GPS para *{label}*.\n"
                    "Estos lugares pueden no tener datos de ubicación en nuestra base de datos.",
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

    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("ayuda",      ayuda))
    app.add_handler(CommandHandler("help",       ayuda))
    app.add_handler(CommandHandler("reset",      reset))
    app.add_handler(CommandHandler("emergencia", emergencia))
    app.add_handler(MessageHandler(filters.LOCATION, manejar_ubicacion))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, manejar_voz))
    app.add_handler(CallbackQueryHandler(manejar_botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot corriendo... Ctrl+C para detener")
    app.run_polling()


if __name__ == "__main__":
    main()
