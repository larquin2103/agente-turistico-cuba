import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

def extraer_coordenadas(texto_documento: str) -> tuple:
    """Extrae lat/lng del texto del documento indexado en ChromaDB"""
    patron = r"Coordenadas GPS:\s*([-\d.]+),\s*([-\d.]+)"
    match = re.search(patron, texto_documento)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def extraer_campo(texto: str, campo: str) -> str:
    """Extrae cualquier campo del texto del documento"""
    patron = rf"{campo}:\s*(.+)"
    match = re.search(patron, texto)
    return match.group(1).strip() if match else ""

def parsear_documento(texto: str) -> dict:
    """Convierte el texto del documento en un diccionario estructurado"""
    return {
        "nombre":      extraer_campo(texto, "Nombre"),
        "direccion":   extraer_campo(texto, "Dirección"),
        "telefono":    extraer_campo(texto, "Teléfono"),
        "rating":      extraer_campo(texto, "Calificación"),
        "horario":     extraer_campo(texto, "Horario"),
        "website":     extraer_campo(texto, "Sitio web"),
        "categoria":   extraer_campo(texto, "Categoría de búsqueda"),
        "lat":         None,
        "lng":         None,
    }

def generar_kml(lugares: list) -> str:
    """
    Genera KML compatible con OsmAnd, Google Earth y Maps.me
    lugares: lista de dicts con nombre, lat, lng, descripcion, etc.
    """
    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")

    nombre_doc = ET.SubElement(doc, "name")
    nombre_doc.text = "Agente Turístico Cuba"

    descripcion_doc = ET.SubElement(doc, "description")
    descripcion_doc.text = f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Estilo del marcador
    style = ET.SubElement(doc, "Style", id="turistico")
    icon_style = ET.SubElement(style, "IconStyle")
    color = ET.SubElement(icon_style, "color")
    color.text = "ff0000ff"  # Rojo en formato ABGR de KML
    scale = ET.SubElement(icon_style, "scale")
    scale.text = "1.2"
    icon = ET.SubElement(icon_style, "Icon")
    href = ET.SubElement(icon, "href")
    href.text = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"

    for lugar in lugares:
        if not lugar.get("lat") or not lugar.get("lng"):
            continue

        placemark = ET.SubElement(doc, "Placemark")

        nm = ET.SubElement(placemark, "name")
        nm.text = lugar.get("nombre", "Sin nombre")

        ET.SubElement(placemark, "styleUrl").text = "#turistico"

        # Descripción enriquecida visible en OsmAnd
        desc_partes = []
        if lugar.get("direccion"):
            desc_partes.append(f"📍 {lugar['direccion']}")
        if lugar.get("telefono"):
            desc_partes.append(f"📞 {lugar['telefono']}")
        if lugar.get("rating"):
            desc_partes.append(f"⭐ {lugar['rating']}")
        if lugar.get("horario"):
            desc_partes.append(f"🕐 {lugar['horario']}")
        if lugar.get("website"):
            desc_partes.append(f"🌐 {lugar['website']}")

        desc = ET.SubElement(placemark, "description")
        desc.text = "\n".join(desc_partes)

        point = ET.SubElement(placemark, "Point")
        coords = ET.SubElement(point, "coordinates")
        coords.text = f"{lugar['lng']},{lugar['lat']},0"

    # Formatear XML con indentación
    xml_str = ET.tostring(kml, encoding="unicode")
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ", encoding=None)

def generar_gpx(lugares: list) -> str:
    """
    Genera GPX compatible con OsmAnd, Garmin, Komoot y cualquier app de navegación
    """
    gpx = ET.Element("gpx",
        version="1.1",
        creator="Agente Turístico Cuba",
        xmlns="http://www.topografix.com/GPX/1/1",
        **{"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
           "xsi:schemaLocation": "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"}
    )

    metadata = ET.SubElement(gpx, "metadata")
    ET.SubElement(metadata, "name").text = "Agente Turístico Cuba"
    ET.SubElement(metadata, "desc").text = "Puntos de interés turístico en Cuba"
    ET.SubElement(metadata, "time").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    for lugar in lugares:
        if not lugar.get("lat") or not lugar.get("lng"):
            continue

        wpt = ET.SubElement(gpx, "wpt",
            lat=str(lugar["lat"]),
            lon=str(lugar["lng"])
        )

        ET.SubElement(wpt, "name").text = lugar.get("nombre", "Sin nombre")

        desc_partes = []
        if lugar.get("direccion"):
            desc_partes.append(f"Dirección: {lugar['direccion']}")
        if lugar.get("telefono"):
            desc_partes.append(f"Teléfono: {lugar['telefono']}")
        if lugar.get("rating"):
            desc_partes.append(f"Rating: {lugar['rating']}")
        if lugar.get("horario"):
            desc_partes.append(f"Horario: {lugar['horario']}")
        if lugar.get("website"):
            desc_partes.append(f"Web: {lugar['website']}")

        ET.SubElement(wpt, "desc").text = " | ".join(desc_partes)
        ET.SubElement(wpt, "type").text = lugar.get("categoria", "Turismo Cuba")

    xml_str = ET.tostring(gpx, encoding="unicode")
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ", encoding=None)