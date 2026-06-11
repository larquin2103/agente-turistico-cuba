import math
import chromadb
import re

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calcula distancia en km entre dos coordenadas GPS"""
    R = 6371  # Radio de la Tierra en km
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def extraer_coordenadas_texto(texto: str) -> tuple:
    """Extrae lat/lng del texto del documento de ChromaDB"""
    patron = r"Coordenadas GPS:\s*([-\d.]+),\s*([-\d.]+)"
    match = re.search(patron, texto)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def extraer_campo(texto: str, campo: str) -> str:
    patron = rf"{campo}:\s*(.+)"
    match = re.search(patron, texto)
    return match.group(1).strip() if match else ""

def lugares_cercanos(lat_usuario: float, lng_usuario: float,
                     db_path: str, top_n: int = 3,
                     categoria_filtro: str = None) -> list:
    """
    Calcula los N lugares más cercanos a la posición del usuario.
    Si se indica categoria_filtro, descarta lugares cuya "Categoría de
    búsqueda" no contenga ese texto (case-insensitive).
    Retorna lista de dicts ordenada por distancia.
    """
    client = chromadb.PersistentClient(path=db_path)
    col = client.get_or_create_collection("lugares_turisticos")
    todos = col.get()

    filtro = categoria_filtro.lower() if categoria_filtro else None

    resultados = []
    for texto in todos["documents"]:
        lat, lng = extraer_coordenadas_texto(texto)
        if lat is None or lng is None:
            continue

        categoria = extraer_campo(texto, "Categoría de búsqueda")
        if filtro and filtro not in categoria.lower():
            continue

        distancia = haversine(lat_usuario, lng_usuario, lat, lng)

        resultados.append({
            "nombre":    extraer_campo(texto, "Nombre"),
            "direccion": extraer_campo(texto, "Dirección"),
            "telefono":  extraer_campo(texto, "Teléfono"),
            "rating":    extraer_campo(texto, "Calificación"),
            "horario":   extraer_campo(texto, "Horario"),
            "website":   extraer_campo(texto, "Sitio web"),
            "categoria": categoria,
            "lat":       lat,
            "lng":       lng,
            "distancia": round(distancia, 2),
        })

    resultados.sort(key=lambda x: x["distancia"])
    return resultados[:top_n]

# Barrios y zonas conocidas de La Habana con coordenadas aproximadas
ZONAS_HABANA = {
    "habana vieja":        (23.1367, -82.3489),
    "centro habana":       (23.1330, -82.3660),
    "vedado":              (23.1333, -82.3833),
    "miramar":             (23.1000, -82.4167),
    "playa":               (23.0833, -82.4500),
    "cerro":               (23.1167, -82.3833),
    "10 de octubre":       (23.1000, -82.3500),
    "san miguel del padron":(23.0833, -82.3167),
    "guanabacoa":          (23.1167, -82.2833),
    "regla":               (23.1333, -82.3333),
    "marianao":            (23.0833, -82.4333),
    "boyeros":             (22.9833, -82.4000),
    "arroyo naranjo":      (23.0333, -82.3500),
    "cotorro":             (23.0333, -82.2833),
    "plaza":               (23.1167, -82.3833),
    "lisa":                (23.0833, -82.4167),
    "revolucion":          (23.1200, -82.3700),
    "malecon":             (23.1467, -82.3600),
}

def texto_a_coordenadas(texto_ubicacion: str) -> tuple:
    """
    Convierte texto de barrio o zona a coordenadas.
    Retorna (lat, lng) o (None, None) si no reconoce el lugar.
    """
    texto_lower = texto_ubicacion.lower().strip()

    # Buscar coincidencia exacta o parcial
    for zona, coords in ZONAS_HABANA.items():
        if zona in texto_lower or texto_lower in zona:
            return coords

    # Buscar palabras clave individuales
    for zona, coords in ZONAS_HABANA.items():
        palabras = zona.split()
        if any(p in texto_lower for p in palabras if len(p) > 4):
            return coords

    return None, None

def formatear_respuesta_cercania(lugares: list, distancia_max_km: float = 50) -> str:
    """Formatea la respuesta del agente con los lugares más cercanos"""
    if not lugares:
        return "No encontré lugares con coordenadas GPS en mi base de datos."

    lugares_filtrados = [l for l in lugares if l["distancia"] <= distancia_max_km]

    if not lugares_filtrados:
        return (
            f"Los lugares más cercanos en mi base de datos están a más de "
            f"{distancia_max_km} km de tu ubicación. No tengo datos para esta zona."
        )

    lineas = ["📍 *Los lugares más cercanos a tu ubicación:*\n"]

    for i, lugar in enumerate(lugares_filtrados, 1):
        dist = lugar["distancia"]
        if dist < 1:
            dist_texto = f"{int(dist * 1000)} metros"
        else:
            dist_texto = f"{dist} km"

        lineas.append(f"*{i}. {lugar['nombre']}* — 🚶 {dist_texto}")
        if lugar.get("direccion"):
            lineas.append(f"   📍 {lugar['direccion']}")
        if lugar.get("telefono"):
            lineas.append(f"   📞 {lugar['telefono']}")
        if lugar.get("rating"):
            lineas.append(f"   ⭐ {lugar['rating']}")
        if lugar.get("horario"):
            lineas.append(f"   🕐 {lugar['horario']}")
        lineas.append("")

    return "\n".join(lineas)