import httpx
import logging
import urllib.parse

UNSPLASH_FALLBACK_CUBA = {
    "restaurante":  "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
    "gastronomia":  "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
    "naturaleza":   "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",
    "parque":       "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",
    "cultura":      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
    "museo":        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
    "transporte":   "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800",
    "auto":         "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800",
    "default":      "https://images.unsplash.com/photo-1500759285222-a95626b934cb?w=800",
}

async def obtener_imagen(thumbnail: str, nombre: str, categoria: str = "") -> str:
    """
    Estrategia en cascada:
    1. Thumbnail del JSON (Google Maps)
    2. Búsqueda en Wikipedia
    3. Imagen genérica por categoría (Unsplash)
    """
    if thumbnail and thumbnail.startswith("http"):
        if await verificar_url(thumbnail):
            logging.info(f"Imagen desde JSON: {nombre}")
            return thumbnail

    imagen_wiki = await buscar_wikipedia(nombre)
    if imagen_wiki:
        logging.info(f"Imagen desde Wikipedia: {nombre}")
        return imagen_wiki

    categoria_lower = categoria.lower()
    for clave, url in UNSPLASH_FALLBACK_CUBA.items():
        if clave in categoria_lower or clave in nombre.lower():
            return url

    return UNSPLASH_FALLBACK_CUBA["default"]


async def verificar_url(url: str) -> bool:
    """Verifica que la URL de imagen responde correctamente."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.head(url, follow_redirects=True)
            return resp.status_code == 200
    except Exception:
        return False


async def buscar_wikipedia(nombre: str) -> str:
    """
    Busca imagen del lugar en Wikipedia API.
    Funciona bien para monumentos, parques y lugares históricos.
    """
    try:
        busqueda_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&list=search&srsearch={urllib.parse.quote(nombre + ' Cuba')}"
            "&format=json&srlimit=1"
        )
        imagen_url_tpl = (
            "https://en.wikipedia.org/w/api.php"
            "?action=query&titles={titulo}"
            "&prop=pageimages&format=json&pithumbsize=800"
        )

        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(busqueda_url)
            data = resp.json()

            resultados = data.get("query", {}).get("search", [])
            if not resultados:
                return None

            titulo = urllib.parse.quote(resultados[0]["title"])
            resp2 = await client.get(imagen_url_tpl.format(titulo=titulo))
            data2 = resp2.json()

        pages = data2.get("query", {}).get("pages", {})
        for page in pages.values():
            thumbnail = page.get("thumbnail", {})
            if thumbnail.get("source"):
                return thumbnail["source"]

        return None

    except Exception as e:
        logging.warning(f"Wikipedia error para {nombre}: {e}")
        return None


def construir_caption(lugar: dict) -> str:
    """Texto que acompaña la imagen en Telegram."""
    partes = [f"*{lugar.get('nombre', 'Sin nombre')}*"]

    if lugar.get("rating"):
        partes.append(f"⭐ {lugar['rating']}")
    if lugar.get("direccion"):
        partes.append(f"📍 {lugar['direccion']}")
    if lugar.get("telefono"):
        partes.append(f"📞 {lugar['telefono']}")
    if lugar.get("horario"):
        partes.append(f"🕐 {lugar['horario']}")

    return "\n".join(partes)


def construir_google_maps_url(lat: float, lng: float, nombre: str) -> str:
    nombre_enc = urllib.parse.quote(nombre)
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={nombre_enc}"
