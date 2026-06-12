"""Localización del bot — textos de interfaz en 6 idiomas."""

IDIOMAS = {
    "es": {"nombre": "Español",   "bandera": "🇪🇸"},
    "en": {"nombre": "English",   "bandera": "🇬🇧"},
    "it": {"nombre": "Italiano",  "bandera": "🇮🇹"},
    "fr": {"nombre": "Français",  "bandera": "🇫🇷"},
    "de": {"nombre": "Deutsch",   "bandera": "🇩🇪"},
    "pt": {"nombre": "Português", "bandera": "🇵🇹"},
}

IDIOMA_DEFAULT = "es"


def idioma_desde_codigo(codigo: str) -> str:
    """Normaliza un código BCP47 (ej. 'en-US', 'pt-BR') a uno de los idiomas soportados."""
    if not codigo:
        return IDIOMA_DEFAULT
    base = codigo.lower().split("-")[0]
    return base if base in IDIOMAS else IDIOMA_DEFAULT


TEXTOS = {

    # ── Selección de idioma ──────────────────────────────────────────────
    "elegir_idioma": {
        "es": "🌐 Elige tu idioma:",
        "en": "🌐 Choose your language:",
        "it": "🌐 Scegli la tua lingua:",
        "fr": "🌐 Choisis ta langue :",
        "de": "🌐 Wähle deine Sprache:",
        "pt": "🌐 Escolha o seu idioma:",
    },
    "idioma_cambiado": {
        "es": "{bandera} Idioma cambiado a *{nombre}*.",
        "en": "{bandera} Language changed to *{nombre}*.",
        "it": "{bandera} Lingua cambiata in *{nombre}*.",
        "fr": "{bandera} Langue changée en *{nombre}*.",
        "de": "{bandera} Sprache geändert auf *{nombre}*.",
        "pt": "{bandera} Idioma alterado para *{nombre}*.",
    },

    # ── /start ────────────────────────────────────────────────────────────
    "boton_compartir_ubicacion": {
        "es": "📍 Compartir mi ubicación",
        "en": "📍 Share my location",
        "it": "📍 Condividi la mia posizione",
        "fr": "📍 Partager ma position",
        "de": "📍 Meinen Standort teilen",
        "pt": "📍 Compartilhar minha localização",
    },
    "start_pie": {
        "es": (
            "📍 Comparte tu ubicación y te muestro lo mejor que tienes cerca\n"
            "❓ /ayuda — todo lo que puedo hacer por ti\n"
            "🆘 /emergencia — números de urgencia en Cuba, por si los necesitas\n"
            "🌐 /idioma — elige tu idioma preferido"
        ),
        "en": (
            "📍 Share your location and I'll show you the best places near you\n"
            "❓ /ayuda — everything I can do for you\n"
            "🆘 /emergencia — emergency numbers in Cuba, just in case\n"
            "🌐 /idioma — choose your preferred language"
        ),
        "it": (
            "📍 Condividi la tua posizione e ti mostro il meglio vicino a te\n"
            "❓ /ayuda — tutto quello che posso fare per te\n"
            "🆘 /emergencia — numeri di emergenza a Cuba, per ogni evenienza\n"
            "🌐 /idioma — scegli la tua lingua preferita"
        ),
        "fr": (
            "📍 Partage ta position et je te montre le meilleur autour de toi\n"
            "❓ /ayuda — tout ce que je peux faire pour toi\n"
            "🆘 /emergencia — numéros d'urgence à Cuba, au cas où\n"
            "🌐 /idioma — choisis ta langue préférée"
        ),
        "de": (
            "📍 Teile deinen Standort und ich zeige dir das Beste in deiner Nähe\n"
            "❓ /ayuda — alles, was ich für dich tun kann\n"
            "🆘 /emergencia — Notfallnummern in Kuba, nur für den Fall\n"
            "🌐 /idioma — wähle deine bevorzugte Sprache"
        ),
        "pt": (
            "📍 Compartilhe sua localização e eu mostro o melhor perto de você\n"
            "❓ /ayuda — tudo o que posso fazer por você\n"
            "🆘 /emergencia — números de emergência em Cuba, só por precaução\n"
            "🌐 /idioma — escolha seu idioma preferido"
        ),
    },

    # ── /ayuda ────────────────────────────────────────────────────────────
    "ayuda_texto": {
        "es": (
            "🇨🇺 *Cuba Travel Guide — ¿Qué puedo hacer?*\n\n"
            "Puedes preguntarme en *cualquier idioma*:\n\n"
            "🍽️ *Gastronomía:*\n"
            "  \"¿Dónde comer en La Habana Vieja?\"\n"
            "  \"Mejores restaurantes cerca del Vedado\"\n\n"
            "🏛️ *Cultura e historia:*\n"
            "  \"¿Qué museos hay en La Habana?\"\n"
            "  \"Monumentos históricos en La Habana\"\n\n"
            "🌿 *Naturaleza:*\n"
            "  \"Parques naturales cerca del Vedado\"\n"
            "  \"¿Dónde puedo ver naturaleza en La Habana?\"\n\n"
            "🚌 *Transporte:*\n"
            "  \"¿Cómo llegar al aeropuerto?\"\n"
            "  \"Alquiler de autos en La Habana\"\n\n"
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
            "  /emergencia — Números de urgencia en Cuba\n"
            "  /idioma — Cambiar idioma\n\n"
            "💡 El bot recuerda el contexto. Puedes preguntar "
            "\"¿Y el horario?\" como seguimiento."
        ),
        "en": (
            "🇨🇺 *Cuba Travel Guide — What can I do?*\n\n"
            "You can ask me in *any language*:\n\n"
            "🍽️ *Food & dining:*\n"
            "  \"Where to eat in Old Havana?\"\n"
            "  \"Best restaurants near Vedado\"\n\n"
            "🏛️ *Culture & history:*\n"
            "  \"What museums are in Havana?\"\n"
            "  \"Historic monuments in Havana\"\n\n"
            "🌿 *Nature:*\n"
            "  \"Natural parks near Vedado\"\n"
            "  \"Where can I see nature in Havana?\"\n\n"
            "🚌 *Transport:*\n"
            "  \"How do I get to the airport?\"\n"
            "  \"Car rental in Havana\"\n\n"
            "📍 *Nearby places:*\n"
            "  Share your GPS location → closest places\n"
            "  \"What's near Vedado?\"\n\n"
            "🗺️ *Offline maps (OsmAnd / Maps.me):*\n"
            "  Download KML or GPX to navigate without internet\n\n"
            "🎙️ *Voice notes:*\n"
            "  Send a voice message with your question, I understand it too\n\n"
            "📋 *Commands:*\n"
            "  /start — Restart\n"
            "  /ayuda — This help\n"
            "  /reset — Clear conversation history\n"
            "  /emergencia — Emergency numbers in Cuba\n"
            "  /idioma — Change language\n\n"
            "💡 The bot remembers context. You can ask "
            "\"And the schedule?\" as a follow-up."
        ),
        "it": (
            "🇨🇺 *Cuba Travel Guide — Cosa posso fare?*\n\n"
            "Puoi chiedermi in *qualsiasi lingua*:\n\n"
            "🍽️ *Gastronomia:*\n"
            "  \"Dove mangiare a L'Avana Vecchia?\"\n"
            "  \"Migliori ristoranti vicino al Vedado\"\n\n"
            "🏛️ *Cultura e storia:*\n"
            "  \"Quali musei ci sono a L'Avana?\"\n"
            "  \"Monumenti storici a L'Avana\"\n\n"
            "🌿 *Natura:*\n"
            "  \"Parchi naturali vicino al Vedado\"\n"
            "  \"Dove posso vedere la natura a L'Avana?\"\n\n"
            "🚌 *Trasporti:*\n"
            "  \"Come arrivare all'aeroporto?\"\n"
            "  \"Noleggio auto a L'Avana\"\n\n"
            "📍 *Luoghi vicini:*\n"
            "  Condividi la tua posizione GPS → i più vicini\n"
            "  \"Cosa c'è vicino al Vedado?\"\n\n"
            "🗺️ *Mappe offline (OsmAnd / Maps.me):*\n"
            "  Scarica KML o GPX per navigare senza internet\n\n"
            "🎙️ *Note vocali:*\n"
            "  Invia un audio con la tua domanda, ti capisco lo stesso\n\n"
            "📋 *Comandi:*\n"
            "  /start — Ricomincia\n"
            "  /ayuda — Questo aiuto\n"
            "  /reset — Cancella la cronologia\n"
            "  /emergencia — Numeri di emergenza a Cuba\n"
            "  /idioma — Cambia lingua\n\n"
            "💡 Il bot ricorda il contesto. Puoi chiedere "
            "\"E l'orario?\" come domanda di follow-up."
        ),
        "fr": (
            "🇨🇺 *Cuba Travel Guide — Que puis-je faire ?*\n\n"
            "Tu peux me poser des questions dans *n'importe quelle langue* :\n\n"
            "🍽️ *Gastronomie :*\n"
            "  \"Où manger à La Havane Vieille ?\"\n"
            "  \"Meilleurs restaurants près du Vedado\"\n\n"
            "🏛️ *Culture et histoire :*\n"
            "  \"Quels musées y a-t-il à La Havane ?\"\n"
            "  \"Monuments historiques à La Havane\"\n\n"
            "🌿 *Nature :*\n"
            "  \"Parcs naturels près du Vedado\"\n"
            "  \"Où voir la nature à La Havane ?\"\n\n"
            "🚌 *Transport :*\n"
            "  \"Comment aller à l'aéroport ?\"\n"
            "  \"Location de voiture à La Havane\"\n\n"
            "📍 *Lieux à proximité :*\n"
            "  Partage ta position GPS → les plus proches\n"
            "  \"Qu'y a-t-il près du Vedado ?\"\n\n"
            "🗺️ *Cartes hors ligne (OsmAnd / Maps.me) :*\n"
            "  Télécharge un KML ou GPX pour naviguer sans internet\n\n"
            "🎙️ *Notes vocales :*\n"
            "  Envoie un audio avec ta question, je te comprends aussi\n\n"
            "📋 *Commandes :*\n"
            "  /start — Redémarrer\n"
            "  /ayuda — Cette aide\n"
            "  /reset — Effacer l'historique\n"
            "  /emergencia — Numéros d'urgence à Cuba\n"
            "  /idioma — Changer de langue\n\n"
            "💡 Le bot se souvient du contexte. Tu peux demander "
            "\"Et l'horaire ?\" en suivi."
        ),
        "de": (
            "🇨🇺 *Cuba Travel Guide — Was kann ich tun?*\n\n"
            "Du kannst mich in *jeder Sprache* fragen:\n\n"
            "🍽️ *Essen & Trinken:*\n"
            "  \"Wo kann man in Alt-Havanna essen?\"\n"
            "  \"Beste Restaurants in der Nähe von Vedado\"\n\n"
            "🏛️ *Kultur & Geschichte:*\n"
            "  \"Welche Museen gibt es in Havanna?\"\n"
            "  \"Historische Denkmäler in Havanna\"\n\n"
            "🌿 *Natur:*\n"
            "  \"Naturparks in der Nähe von Vedado\"\n"
            "  \"Wo kann ich Natur in Havanna sehen?\"\n\n"
            "🚌 *Transport:*\n"
            "  \"Wie komme ich zum Flughafen?\"\n"
            "  \"Autovermietung in Havanna\"\n\n"
            "📍 *Orte in der Nähe:*\n"
            "  Teile deinen GPS-Standort → die nächstgelegenen\n"
            "  \"Was gibt es in der Nähe von Vedado?\"\n\n"
            "🗺️ *Offline-Karten (OsmAnd / Maps.me):*\n"
            "  Lade KML oder GPX herunter, um ohne Internet zu navigieren\n\n"
            "🎙️ *Sprachnachrichten:*\n"
            "  Sende eine Sprachnachricht mit deiner Frage, ich verstehe sie auch\n\n"
            "📋 *Befehle:*\n"
            "  /start — Neu starten\n"
            "  /ayuda — Diese Hilfe\n"
            "  /reset — Gesprächsverlauf löschen\n"
            "  /emergencia — Notfallnummern in Kuba\n"
            "  /idioma — Sprache ändern\n\n"
            "💡 Der Bot merkt sich den Kontext. Du kannst als Folgefrage "
            "\"Und die Öffnungszeiten?\" fragen."
        ),
        "pt": (
            "🇨🇺 *Cuba Travel Guide — O que posso fazer?*\n\n"
            "Você pode me perguntar em *qualquer idioma*:\n\n"
            "🍽️ *Gastronomia:*\n"
            "  \"Onde comer em Havana Velha?\"\n"
            "  \"Melhores restaurantes perto do Vedado\"\n\n"
            "🏛️ *Cultura e história:*\n"
            "  \"Quais museus há em Havana?\"\n"
            "  \"Monumentos históricos em Havana\"\n\n"
            "🌿 *Natureza:*\n"
            "  \"Parques naturais perto do Vedado\"\n"
            "  \"Onde posso ver natureza em Havana?\"\n\n"
            "🚌 *Transporte:*\n"
            "  \"Como chegar ao aeroporto?\"\n"
            "  \"Aluguel de carros em Havana\"\n\n"
            "📍 *Lugares próximos:*\n"
            "  Compartilhe sua localização GPS → os mais próximos\n"
            "  \"O que há perto do Vedado?\"\n\n"
            "🗺️ *Mapas offline (OsmAnd / Maps.me):*\n"
            "  Baixe KML ou GPX para navegar sem internet\n\n"
            "🎙️ *Notas de voz:*\n"
            "  Envie um áudio com sua pergunta, eu também entendo\n\n"
            "📋 *Comandos:*\n"
            "  /start — Reiniciar\n"
            "  /ayuda — Esta ajuda\n"
            "  /reset — Apagar histórico de conversa\n"
            "  /emergencia — Números de emergência em Cuba\n"
            "  /idioma — Mudar idioma\n\n"
            "💡 O bot lembra o contexto. Você pode perguntar "
            "\"E o horário?\" como continuação."
        ),
    },

    # ── /emergencia ───────────────────────────────────────────────────────
    "emergencia_texto": {
        "es": (
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
            "  +53 7 866-4499 | asisttur.cu"
        ),
        "en": (
            "🆘 *Emergencies in Cuba*\n\n"
            "🚒 Fire department: *105*\n"
            "🚓 Police: *106*\n"
            "🚑 Ambulance / Emergencies: *104*\n"
            "⚡ Power outage: *185*\n\n"
            "🏥 *Hospitals for foreigners — Havana:*\n\n"
            "• *Cira García* (CIMEX)\n"
            "  📍 Calle 20 No. 4101 esq. 41, Miramar\n"
            "  📞 +53 7 204-2811\n\n"
            "• *Hermanos Ameijeiras*\n"
            "  📍 San Lázaro 701, Centro Habana\n"
            "  📞 +53 7 876-1000\n\n"
            "💱 *Currency exchange (CADECA):*\n"
            "  • Obispo y Cuba, Old Havana\n"
            "  • Hotel Nacional, Vedado\n"
            "  • José Martí Airport\n\n"
            "📞 *Asisttur* (tourist assistance):\n"
            "  +53 7 866-4499 | asisttur.cu"
        ),
        "it": (
            "🆘 *Emergenze a Cuba*\n\n"
            "🚒 Vigili del fuoco: *105*\n"
            "🚓 Polizia: *106*\n"
            "🚑 Ambulanza / Emergenze: *104*\n"
            "⚡ Guasto elettrico: *185*\n\n"
            "🏥 *Ospedali per stranieri — L'Avana:*\n\n"
            "• *Cira García* (CIMEX)\n"
            "  📍 Calle 20 No. 4101 esq. 41, Miramar\n"
            "  📞 +53 7 204-2811\n\n"
            "• *Hermanos Ameijeiras*\n"
            "  📍 San Lázaro 701, Centro Habana\n"
            "  📞 +53 7 876-1000\n\n"
            "💱 *Cambio valuta (CADECA):*\n"
            "  • Obispo y Cuba, L'Avana Vecchia\n"
            "  • Hotel Nacional, Vedado\n"
            "  • Aeroporto José Martí\n\n"
            "📞 *Asisttur* (assistenza turisti):\n"
            "  +53 7 866-4499 | asisttur.cu"
        ),
        "fr": (
            "🆘 *Urgences à Cuba*\n\n"
            "🚒 Pompiers : *105*\n"
            "🚓 Police : *106*\n"
            "🚑 Ambulance / Urgences : *104*\n"
            "⚡ Panne électrique : *185*\n\n"
            "🏥 *Hôpitaux pour étrangers — La Havane :*\n\n"
            "• *Cira García* (CIMEX)\n"
            "  📍 Calle 20 No. 4101 esq. 41, Miramar\n"
            "  📞 +53 7 204-2811\n\n"
            "• *Hermanos Ameijeiras*\n"
            "  📍 San Lázaro 701, Centro Habana\n"
            "  📞 +53 7 876-1000\n\n"
            "💱 *Bureaux de change (CADECA) :*\n"
            "  • Obispo y Cuba, La Vieille Havane\n"
            "  • Hôtel Nacional, Vedado\n"
            "  • Aéroport José Martí\n\n"
            "📞 *Asisttur* (assistance touristique) :\n"
            "  +53 7 866-4499 | asisttur.cu"
        ),
        "de": (
            "🆘 *Notfälle in Kuba*\n\n"
            "🚒 Feuerwehr: *105*\n"
            "🚓 Polizei: *106*\n"
            "🚑 Krankenwagen / Notfälle: *104*\n"
            "⚡ Stromausfall: *185*\n\n"
            "🏥 *Krankenhäuser für Ausländer — Havanna:*\n\n"
            "• *Cira García* (CIMEX)\n"
            "  📍 Calle 20 No. 4101 esq. 41, Miramar\n"
            "  📞 +53 7 204-2811\n\n"
            "• *Hermanos Ameijeiras*\n"
            "  📍 San Lázaro 701, Centro Habana\n"
            "  📞 +53 7 876-1000\n\n"
            "💱 *Wechselstuben (CADECA):*\n"
            "  • Obispo y Cuba, Alt-Havanna\n"
            "  • Hotel Nacional, Vedado\n"
            "  • Flughafen José Martí\n\n"
            "📞 *Asisttur* (Touristenhilfe):\n"
            "  +53 7 866-4499 | asisttur.cu"
        ),
        "pt": (
            "🆘 *Emergências em Cuba*\n\n"
            "🚒 Bombeiros: *105*\n"
            "🚓 Polícia: *106*\n"
            "🚑 Ambulância / Emergências: *104*\n"
            "⚡ Falta de energia: *185*\n\n"
            "🏥 *Hospitais para estrangeiros — Havana:*\n\n"
            "• *Cira García* (CIMEX)\n"
            "  📍 Calle 20 No. 4101 esq. 41, Miramar\n"
            "  📞 +53 7 204-2811\n\n"
            "• *Hermanos Ameijeiras*\n"
            "  📍 San Lázaro 701, Centro Habana\n"
            "  📞 +53 7 876-1000\n\n"
            "💱 *Casas de câmbio (CADECA):*\n"
            "  • Obispo y Cuba, Havana Velha\n"
            "  • Hotel Nacional, Vedado\n"
            "  • Aeroporto José Martí\n\n"
            "📞 *Asisttur* (assistência ao turista):\n"
            "  +53 7 866-4499 | asisttur.cu"
        ),
    },

    # ── /reset ────────────────────────────────────────────────────────────
    "reset_confirmacion": {
        "es": "🔄 Conversación reiniciada. ¡Hola de nuevo!\n¿En qué puedo ayudarte hoy? 🇨🇺",
        "en": "🔄 Conversation reset. Hello again!\nHow can I help you today? 🇨🇺",
        "it": "🔄 Conversazione riavviata. Ciao di nuovo!\nCome posso aiutarti oggi? 🇨🇺",
        "fr": "🔄 Conversation réinitialisée. Bonjour à nouveau !\nComment puis-je t'aider aujourd'hui ? 🇨🇺",
        "de": "🔄 Unterhaltung zurückgesetzt. Hallo nochmal!\nWie kann ich dir heute helfen? 🇨🇺",
        "pt": "🔄 Conversa reiniciada. Olá novamente!\nComo posso ajudar hoje? 🇨🇺",
    },

    # ── Ubicación / cercanía ──────────────────────────────────────────────
    "ubicacion_recibida": {
        "es": "📡 Ubicación recibida. Buscando lugares cercanos...",
        "en": "📡 Location received. Looking for nearby places...",
        "it": "📡 Posizione ricevuta. Cerco luoghi vicini...",
        "fr": "📡 Position reçue. Recherche de lieux à proximité...",
        "de": "📡 Standort empfangen. Suche nach Orten in der Nähe...",
        "pt": "📡 Localização recebida. Procurando lugares próximos...",
    },
    "pregunta_mapa_offline": {
        "es": "¿Quieres el mapa para navegar sin internet?",
        "en": "Would you like the map to navigate offline?",
        "it": "Vuoi la mappa per navigare senza internet?",
        "fr": "Veux-tu la carte pour naviguer sans internet ?",
        "de": "Möchtest du die Karte zur Offline-Navigation?",
        "pt": "Quer o mapa para navegar sem internet?",
    },
    "boton_kml_n": {
        "es": "🗺️ KML ({n} lugares)",
        "en": "🗺️ KML ({n} places)",
        "it": "🗺️ KML ({n} luoghi)",
        "fr": "🗺️ KML ({n} lieux)",
        "de": "🗺️ KML ({n} Orte)",
        "pt": "🗺️ KML ({n} lugares)",
    },
    "boton_gpx_n": {
        "es": "📍 GPX ({n} lugares)",
        "en": "📍 GPX ({n} places)",
        "it": "📍 GPX ({n} luoghi)",
        "fr": "📍 GPX ({n} lieux)",
        "de": "📍 GPX ({n} Orte)",
        "pt": "📍 GPX ({n} lugares)",
    },
    "n_lugares": {
        "es": "{n} lugares",
        "en": "{n} places",
        "it": "{n} luoghi",
        "fr": "{n} lieux",
        "de": "{n} Orte",
        "pt": "{n} lugares",
    },
    "sin_datos_zona": {
        "es": "📭 No tengo datos de tu zona en mi base de datos.\n🔍 Buscando lugares cercanos en internet...",
        "en": "📭 I don't have data for your area in my database.\n🔍 Searching for nearby places online...",
        "it": "📭 Non ho dati della tua zona nel mio database.\n🔍 Cerco luoghi vicini su internet...",
        "fr": "📭 Je n'ai pas de données sur ta zone dans ma base.\n🔍 Recherche de lieux à proximité sur internet...",
        "de": "📭 Ich habe keine Daten für deine Gegend in meiner Datenbank.\n🔍 Suche nach Orten in der Nähe im Internet...",
        "pt": "📭 Não tenho dados da sua região no meu banco de dados.\n🔍 Procurando lugares próximos na internet...",
    },
    "sin_datos_zona_pregunta": {
        "es": "📭 No tengo datos de esa zona en mi base de datos.\n🔍 Buscando en internet...",
        "en": "📭 I don't have data for that area in my database.\n🔍 Searching online...",
        "it": "📭 Non ho dati di quella zona nel mio database.\n🔍 Cerco su internet...",
        "fr": "📭 Je n'ai pas de données sur cette zone dans ma base.\n🔍 Recherche sur internet...",
        "de": "📭 Ich habe keine Daten für diese Gegend in meiner Datenbank.\n🔍 Suche im Internet...",
        "pt": "📭 Não tenho dados dessa região no meu banco de dados.\n🔍 Procurando na internet...",
    },
    "compartir_ubicacion_para_buscar": {
        "es": "Para buscar en internet comparte tu ubicación GPS con el botón 📎 → Ubicación.",
        "en": "To search online, share your GPS location using the 📎 → Location button.",
        "it": "Per cercare su internet condividi la tua posizione GPS con il pulsante 📎 → Posizione.",
        "fr": "Pour rechercher sur internet, partage ta position GPS via le bouton 📎 → Position.",
        "de": "Um online zu suchen, teile deinen GPS-Standort über die Schaltfläche 📎 → Standort.",
        "pt": "Para buscar na internet, compartilhe sua localização GPS com o botão 📎 → Localização.",
    },
    "pregunta_mapa_multi": {
        "es": "🗺️ ¿Quieres un mapa con los *{n} lugares* mencionados?",
        "en": "🗺️ Would you like a map with the *{n} places* mentioned?",
        "it": "🗺️ Vuoi una mappa con i *{n} luoghi* menzionati?",
        "fr": "🗺️ Veux-tu une carte avec les *{n} lieux* mentionnés ?",
        "de": "🗺️ Möchtest du eine Karte mit den *{n} genannten Orten*?",
        "pt": "🗺️ Quer um mapa com os *{n} lugares* mencionados?",
    },
    "mapa_de_lugar": {
        "es": "🗺️ Aquí tienes el mapa offline de *{nombre}*. Elige el formato:",
        "en": "🗺️ Here's the offline map for *{nombre}*. Choose a format:",
        "it": "🗺️ Ecco la mappa offline di *{nombre}*. Scegli il formato:",
        "fr": "🗺️ Voici la carte hors ligne de *{nombre}*. Choisis le format :",
        "de": "🗺️ Hier ist die Offline-Karte für *{nombre}*. Wähle das Format:",
        "pt": "🗺️ Aqui está o mapa offline de *{nombre}*. Escolha o formato:",
    },

    # ── Errores genéricos ─────────────────────────────────────────────────
    "error_conexion_api": {
        "es": "⚠️ No puedo conectarme al servidor. Asegúrate de que la API está corriendo.",
        "en": "⚠️ I can't connect to the server. Make sure the API is running.",
        "it": "⚠️ Non riesco a connettermi al server. Assicurati che l'API sia in esecuzione.",
        "fr": "⚠️ Je ne peux pas me connecter au serveur. Assure-toi que l'API fonctionne.",
        "de": "⚠️ Ich kann keine Verbindung zum Server herstellen. Stelle sicher, dass die API läuft.",
        "pt": "⚠️ Não consigo me conectar ao servidor. Verifique se a API está em execução.",
    },
    "error_conexion_api_largo": {
        "es": "⚠️ No puedo conectarme al servidor. ¿Está la API corriendo?\nIntenta de nuevo en unos momentos.",
        "en": "⚠️ I can't connect to the server. Is the API running?\nPlease try again in a moment.",
        "it": "⚠️ Non riesco a connettermi al server. L'API è in esecuzione?\nRiprova tra un momento.",
        "fr": "⚠️ Je ne peux pas me connecter au serveur. L'API fonctionne-t-elle ?\nRéessaie dans un instant.",
        "de": "⚠️ Ich kann keine Verbindung zum Server herstellen. Läuft die API?\nVersuche es gleich noch einmal.",
        "pt": "⚠️ Não consigo me conectar ao servidor. A API está rodando?\nTente novamente em instantes.",
    },
    "error_cercanos": {
        "es": "Error buscando lugares cercanos. Intenta de nuevo.",
        "en": "Error searching for nearby places. Please try again.",
        "it": "Errore nella ricerca di luoghi vicini. Riprova.",
        "fr": "Erreur lors de la recherche de lieux à proximité. Réessaie.",
        "de": "Fehler bei der Suche nach Orten in der Nähe. Bitte versuche es erneut.",
        "pt": "Erro ao buscar lugares próximos. Tente novamente.",
    },
    "rate_limit": {
        "es": "⏱️ Demasiadas consultas seguidas. Espera un momento e intenta de nuevo.",
        "en": "⏱️ Too many requests in a row. Wait a moment and try again.",
        "it": "⏱️ Troppe richieste consecutive. Aspetta un momento e riprova.",
        "fr": "⏱️ Trop de requêtes consécutives. Attends un instant et réessaie.",
        "de": "⏱️ Zu viele Anfragen hintereinander. Warte einen Moment und versuche es erneut.",
        "pt": "⏱️ Muitas solicitações seguidas. Aguarde um momento e tente novamente.",
    },
    "timeout": {
        "es": "⏳ La consulta tardó demasiado. Por favor intenta de nuevo.",
        "en": "⏳ The request took too long. Please try again.",
        "it": "⏳ La richiesta ha impiegato troppo tempo. Riprova.",
        "fr": "⏳ La requête a pris trop de temps. Réessaie s'il te plaît.",
        "de": "⏳ Die Anfrage hat zu lange gedauert. Bitte versuche es erneut.",
        "pt": "⏳ A consulta demorou demais. Tente novamente.",
    },
    "limite_groq": {
        "es": "⏱️ Hemos alcanzado el límite de consultas. Espera un momento e intenta de nuevo.",
        "en": "⏱️ We've reached the request limit. Wait a moment and try again.",
        "it": "⏱️ Abbiamo raggiunto il limite di richieste. Aspetta un momento e riprova.",
        "fr": "⏱️ Nous avons atteint la limite de requêtes. Attends un instant et réessaie.",
        "de": "⏱️ Wir haben das Anfragelimit erreicht. Warte einen Moment und versuche es erneut.",
        "pt": "⏱️ Atingimos o limite de consultas. Aguarde um momento e tente novamente.",
    },
    "error_servidor": {
        "es": "Lo siento, ocurrió un error en el servidor. Por favor intenta de nuevo.",
        "en": "Sorry, a server error occurred. Please try again.",
        "it": "Mi dispiace, si è verificato un errore sul server. Riprova.",
        "fr": "Désolé, une erreur serveur s'est produite. Réessaie s'il te plaît.",
        "de": "Entschuldigung, es ist ein Serverfehler aufgetreten. Bitte versuche es erneut.",
        "pt": "Desculpe, ocorreu um erro no servidor. Tente novamente.",
    },
    "error_inesperado": {
        "es": "Lo siento, ocurrió un error inesperado. Por favor intenta de nuevo.",
        "en": "Sorry, an unexpected error occurred. Please try again.",
        "it": "Mi dispiace, si è verificato un errore imprevisto. Riprova.",
        "fr": "Désolé, une erreur inattendue s'est produite. Réessaie s'il te plaît.",
        "de": "Entschuldigung, ein unerwarteter Fehler ist aufgetreten. Bitte versuche es erneut.",
        "pt": "Desculpe, ocorreu um erro inesperado. Tente novamente.",
    },

    # ── Voz ───────────────────────────────────────────────────────────────
    "transcribiendo": {
        "es": "🎙️ Transcribiendo audio...",
        "en": "🎙️ Transcribing audio...",
        "it": "🎙️ Trascrizione audio in corso...",
        "fr": "🎙️ Transcription de l'audio...",
        "de": "🎙️ Audio wird transkribiert...",
        "pt": "🎙️ Transcrevendo áudio...",
    },
    "audio_no_entendido": {
        "es": "No pude entender el audio. Intenta de nuevo o escribe tu pregunta.",
        "en": "I couldn't understand the audio. Please try again or type your question.",
        "it": "Non sono riuscito a capire l'audio. Riprova o scrivi la tua domanda.",
        "fr": "Je n'ai pas pu comprendre l'audio. Réessaie ou écris ta question.",
        "de": "Ich konnte das Audio nicht verstehen. Versuche es erneut oder schreibe deine Frage.",
        "pt": "Não consegui entender o áudio. Tente novamente ou digite sua pergunta.",
    },
    "escuche": {
        "es": "🎙️ _Escuché:_ \"{texto}\"",
        "en": "🎙️ _I heard:_ \"{texto}\"",
        "it": "🎙️ _Ho sentito:_ \"{texto}\"",
        "fr": "🎙️ _J'ai entendu :_ \"{texto}\"",
        "de": "🎙️ _Ich habe gehört:_ \"{texto}\"",
        "pt": "🎙️ _Ouvi:_ \"{texto}\"",
    },
    "limite_transcripcion": {
        "es": "⏱️ Hemos alcanzado el límite de transcripciones. Intenta de nuevo en unos momentos.",
        "en": "⏱️ We've reached the transcription limit. Please try again in a moment.",
        "it": "⏱️ Abbiamo raggiunto il limite di trascrizioni. Riprova tra un momento.",
        "fr": "⏱️ Nous avons atteint la limite de transcriptions. Réessaie dans un instant.",
        "de": "⏱️ Wir haben das Transkriptionslimit erreicht. Versuche es gleich noch einmal.",
        "pt": "⏱️ Atingimos o limite de transcrições. Tente novamente em instantes.",
    },
    "error_audio": {
        "es": "No pude procesar el audio. Intenta de nuevo.",
        "en": "I couldn't process the audio. Please try again.",
        "it": "Non sono riuscito a elaborare l'audio. Riprova.",
        "fr": "Je n'ai pas pu traiter l'audio. Réessaie.",
        "de": "Ich konnte das Audio nicht verarbeiten. Bitte versuche es erneut.",
        "pt": "Não consegui processar o áudio. Tente novamente.",
    },

    # ── Tarjetas de lugar ─────────────────────────────────────────────────
    "boton_sitio_web": {
        "es": "🌐 Sitio web oficial",
        "en": "🌐 Official website",
        "it": "🌐 Sito web ufficiale",
        "fr": "🌐 Site web officiel",
        "de": "🌐 Offizielle Website",
        "pt": "🌐 Site oficial",
    },
    "boton_google_maps": {
        "es": "📍 Ver en Google Maps",
        "en": "📍 View on Google Maps",
        "it": "📍 Vedi su Google Maps",
        "fr": "📍 Voir sur Google Maps",
        "de": "📍 Auf Google Maps ansehen",
        "pt": "📍 Ver no Google Maps",
    },
    "boton_kml_offline": {
        "es": "🗺️ KML offline",
        "en": "🗺️ Offline KML",
        "it": "🗺️ KML offline",
        "fr": "🗺️ KML hors ligne",
        "de": "🗺️ KML offline",
        "pt": "🗺️ KML offline",
    },
    "boton_gpx_offline": {
        "es": "📍 GPX offline",
        "en": "📍 Offline GPX",
        "it": "📍 GPX offline",
        "fr": "📍 GPX hors ligne",
        "de": "📍 GPX offline",
        "pt": "📍 GPX offline",
    },

    # ── Búsqueda externa (Overpass) ───────────────────────────────────────
    "busqueda_externa_no_disponible": {
        "es": "🔍 La búsqueda externa no está disponible en este momento.\n📍 Explora el área en Google Maps:\n{url}",
        "en": "🔍 External search is not available right now.\n📍 Explore the area on Google Maps:\n{url}",
        "it": "🔍 La ricerca esterna non è disponibile al momento.\n📍 Esplora la zona su Google Maps:\n{url}",
        "fr": "🔍 La recherche externe n'est pas disponible pour le moment.\n📍 Explore la zone sur Google Maps :\n{url}",
        "de": "🔍 Die externe Suche ist derzeit nicht verfügbar.\n📍 Erkunde das Gebiet auf Google Maps:\n{url}",
        "pt": "🔍 A busca externa não está disponível no momento.\n📍 Explore a área no Google Maps:\n{url}",
    },
    "sin_resultados_radio": {
        "es": "🔍 No encontré lugares en un radio de {radio_km:.0f} km.\n📍 Explora la zona en Google Maps:\n{url}",
        "en": "🔍 I couldn't find places within {radio_km:.0f} km.\n📍 Explore the area on Google Maps:\n{url}",
        "it": "🔍 Non ho trovato luoghi entro {radio_km:.0f} km.\n📍 Esplora la zona su Google Maps:\n{url}",
        "fr": "🔍 Je n'ai trouvé aucun lieu dans un rayon de {radio_km:.0f} km.\n📍 Explore la zone sur Google Maps :\n{url}",
        "de": "🔍 Ich habe keine Orte in einem Umkreis von {radio_km:.0f} km gefunden.\n📍 Erkunde das Gebiet auf Google Maps:\n{url}",
        "pt": "🔍 Não encontrei lugares num raio de {radio_km:.0f} km.\n📍 Explore a área no Google Maps:\n{url}",
    },
    "boton_ampliar_radio": {
        "es": "🔍 Ampliar búsqueda a 3 km",
        "en": "🔍 Expand search to 3 km",
        "it": "🔍 Amplia la ricerca a 3 km",
        "fr": "🔍 Élargir la recherche à 3 km",
        "de": "🔍 Suche auf 3 km erweitern",
        "pt": "🔍 Ampliar busca para 3 km",
    },
    "resultados_externos_titulo": {
        "es": "🔍 *Resultados de búsqueda en internet (OpenStreetMap):*\n\n_Datos públicos de OpenStreetMap._\n",
        "en": "🔍 *Search results from the internet (OpenStreetMap):*\n\n_Public data from OpenStreetMap._\n",
        "it": "🔍 *Risultati della ricerca su internet (OpenStreetMap):*\n\n_Dati pubblici di OpenStreetMap._\n",
        "fr": "🔍 *Résultats de recherche sur internet (OpenStreetMap) :*\n\n_Données publiques d'OpenStreetMap._\n",
        "de": "🔍 *Suchergebnisse aus dem Internet (OpenStreetMap):*\n\n_Öffentliche Daten von OpenStreetMap._\n",
        "pt": "🔍 *Resultados de busca na internet (OpenStreetMap):*\n\n_Dados públicos do OpenStreetMap._\n",
    },
    "pregunta_descargar_mapa": {
        "es": "¿Quieres descargar el mapa para navegar sin internet?",
        "en": "Would you like to download the map to navigate offline?",
        "it": "Vuoi scaricare la mappa per navigare senza internet?",
        "fr": "Veux-tu télécharger la carte pour naviguer sans internet ?",
        "de": "Möchtest du die Karte für die Offline-Navigation herunterladen?",
        "pt": "Quer baixar o mapa para navegar sem internet?",
    },
    "busqueda_externa_timeout": {
        "es": "⏳ La búsqueda externa tardó demasiado.\n📍 Explora la zona en: {url}",
        "en": "⏳ The external search took too long.\n📍 Explore the area at: {url}",
        "it": "⏳ La ricerca esterna ha impiegato troppo tempo.\n📍 Esplora la zona su: {url}",
        "fr": "⏳ La recherche externe a pris trop de temps.\n📍 Explore la zone sur : {url}",
        "de": "⏳ Die externe Suche hat zu lange gedauert.\n📍 Erkunde das Gebiet unter: {url}",
        "pt": "⏳ A busca externa demorou demais.\n📍 Explore a área em: {url}",
    },
    "busqueda_externa_error": {
        "es": "🔍 No pude completar la búsqueda externa.\n📍 Explora el área en: {url}",
        "en": "🔍 I couldn't complete the external search.\n📍 Explore the area at: {url}",
        "it": "🔍 Non sono riuscito a completare la ricerca esterna.\n📍 Esplora la zona su: {url}",
        "fr": "🔍 Je n'ai pas pu terminer la recherche externe.\n📍 Explore la zone sur : {url}",
        "de": "🔍 Ich konnte die externe Suche nicht abschließen.\n📍 Erkunde das Gebiet unter: {url}",
        "pt": "🔍 Não consegui concluir a busca externa.\n📍 Explore a área em: {url}",
    },

    # ── Botones / callbacks ───────────────────────────────────────────────
    "ampliando_radio": {
        "es": "🔍 Ampliando búsqueda a 3 km...",
        "en": "🔍 Expanding search to 3 km...",
        "it": "🔍 Ampliamento della ricerca a 3 km...",
        "fr": "🔍 Élargissement de la recherche à 3 km...",
        "de": "🔍 Suche wird auf 3 km erweitert...",
        "pt": "🔍 Ampliando a busca para 3 km...",
    },
    "instrucciones_offline": {
        "es": (
            "📱 *Cómo usar en OsmAnd / Maps.me:*\n"
            "1. Descarga el archivo\n"
            "2. Abre OsmAnd o Maps.me\n"
            "3. Menú → Mis lugares → Importar\n"
            "4. Selecciona el archivo\n"
            "5. ¡Navega sin internet! 🗺️"
        ),
        "en": (
            "📱 *How to use in OsmAnd / Maps.me:*\n"
            "1. Download the file\n"
            "2. Open OsmAnd or Maps.me\n"
            "3. Menu → My places → Import\n"
            "4. Select the file\n"
            "5. Navigate offline! 🗺️"
        ),
        "it": (
            "📱 *Come usare in OsmAnd / Maps.me:*\n"
            "1. Scarica il file\n"
            "2. Apri OsmAnd o Maps.me\n"
            "3. Menu → I miei luoghi → Importa\n"
            "4. Seleziona il file\n"
            "5. Naviga senza internet! 🗺️"
        ),
        "fr": (
            "📱 *Comment utiliser dans OsmAnd / Maps.me :*\n"
            "1. Télécharge le fichier\n"
            "2. Ouvre OsmAnd ou Maps.me\n"
            "3. Menu → Mes lieux → Importer\n"
            "4. Sélectionne le fichier\n"
            "5. Navigue sans internet ! 🗺️"
        ),
        "de": (
            "📱 *So verwendest du es in OsmAnd / Maps.me:*\n"
            "1. Datei herunterladen\n"
            "2. OsmAnd oder Maps.me öffnen\n"
            "3. Menü → Meine Orte → Importieren\n"
            "4. Datei auswählen\n"
            "5. Offline navigieren! 🗺️"
        ),
        "pt": (
            "📱 *Como usar no OsmAnd / Maps.me:*\n"
            "1. Baixe o arquivo\n"
            "2. Abra o OsmAnd ou Maps.me\n"
            "3. Menu → Meus lugares → Importar\n"
            "4. Selecione o arquivo\n"
            "5. Navegue sem internet! 🗺️"
        ),
    },
    "sin_datos_mapa": {
        "es": "No hay datos para generar el mapa.",
        "en": "There's no data to generate the map.",
        "it": "Non ci sono dati per generare la mappa.",
        "fr": "Il n'y a pas de données pour générer la carte.",
        "de": "Es gibt keine Daten, um die Karte zu erstellen.",
        "pt": "Não há dados para gerar o mapa.",
    },
    "generando_mapa": {
        "es": "⏳ Generando {formato} para *{label}*...",
        "en": "⏳ Generating {formato} for *{label}*...",
        "it": "⏳ Generazione di {formato} per *{label}*...",
        "fr": "⏳ Génération du {formato} pour *{label}*...",
        "de": "⏳ {formato} wird für *{label}* erstellt...",
        "pt": "⏳ Gerando {formato} para *{label}*...",
    },
    "error_mapa_externo": {
        "es": "Error generando el mapa externo. Intenta de nuevo.",
        "en": "Error generating the external map. Please try again.",
        "it": "Errore nella generazione della mappa esterna. Riprova.",
        "fr": "Erreur lors de la génération de la carte externe. Réessaie.",
        "de": "Fehler beim Erstellen der externen Karte. Bitte versuche es erneut.",
        "pt": "Erro ao gerar o mapa externo. Tente novamente.",
    },
    "lugar_no_identificado": {
        "es": "No pude identificar el lugar. Pregunta de nuevo.",
        "en": "I couldn't identify the place. Please ask again.",
        "it": "Non sono riuscito a identificare il luogo. Chiedi di nuovo.",
        "fr": "Je n'ai pas pu identifier le lieu. Pose la question à nouveau.",
        "de": "Ich konnte den Ort nicht identifizieren. Bitte frage erneut.",
        "pt": "Não consegui identificar o lugar. Pergunte novamente.",
    },
    "sin_coordenadas": {
        "es": "No encontré coordenadas GPS para *{label}*.\nEstos lugares pueden no tener datos de ubicación en nuestra base de datos.",
        "en": "I couldn't find GPS coordinates for *{label}*.\nThese places may not have location data in our database.",
        "it": "Non ho trovato coordinate GPS per *{label}*.\nQuesti luoghi potrebbero non avere dati di posizione nel nostro database.",
        "fr": "Je n'ai pas trouvé de coordonnées GPS pour *{label}*.\nCes lieux n'ont peut-être pas de données de position dans notre base.",
        "de": "Ich konnte keine GPS-Koordinaten für *{label}* finden.\nDiese Orte haben möglicherweise keine Standortdaten in unserer Datenbank.",
        "pt": "Não encontrei coordenadas GPS para *{label}*.\nEsses lugares podem não ter dados de localização em nosso banco de dados.",
    },
    "error_archivo": {
        "es": "Error generando el archivo. Intenta de nuevo.",
        "en": "Error generating the file. Please try again.",
        "it": "Errore nella generazione del file. Riprova.",
        "fr": "Erreur lors de la génération du fichier. Réessaie.",
        "de": "Fehler beim Erstellen der Datei. Bitte versuche es erneut.",
        "pt": "Erro ao gerar o arquivo. Tente novamente.",
    },
}


def t(clave: str, idioma: str = IDIOMA_DEFAULT, **kwargs) -> str:
    """Devuelve el texto traducido para `clave` en `idioma` (con fallback a IDIOMA_DEFAULT)."""
    entrada = TEXTOS.get(clave, {})
    texto   = entrada.get(idioma) or entrada.get(IDIOMA_DEFAULT) or clave
    if kwargs:
        return texto.format(**kwargs)
    return texto


# ── Etiquetas de tipo de lugar (resultados de OpenStreetMap) ────────────────

TIPO_LABELS = {
    "restaurant":       {"es": "Restaurante",          "en": "Restaurant",        "it": "Ristorante",         "fr": "Restaurant",        "de": "Restaurant",        "pt": "Restaurante"},
    "cafe":             {"es": "Cafetería",            "en": "Café",              "it": "Caffè",               "fr": "Café",              "de": "Café",              "pt": "Café"},
    "bar":              {"es": "Bar",                  "en": "Bar",               "it": "Bar",                 "fr": "Bar",               "de": "Bar",               "pt": "Bar"},
    "pub":              {"es": "Bar",                  "en": "Pub",               "it": "Pub",                 "fr": "Pub",               "de": "Kneipe",            "pt": "Pub"},
    "fast_food":        {"es": "Comida rápida",        "en": "Fast food",         "it": "Fast food",           "fr": "Restauration rapide", "de": "Fast Food",       "pt": "Comida rápida"},
    "museum":           {"es": "Museo",                "en": "Museum",            "it": "Museo",               "fr": "Musée",             "de": "Museum",            "pt": "Museu"},
    "hotel":            {"es": "Hotel",                "en": "Hotel",             "it": "Hotel",               "fr": "Hôtel",             "de": "Hotel",             "pt": "Hotel"},
    "hostel":           {"es": "Hostal",               "en": "Hostel",            "it": "Ostello",             "fr": "Auberge",           "de": "Hostel",            "pt": "Hostel"},
    "guest_house":      {"es": "Casa huésped",         "en": "Guest house",       "it": "Casa per ospiti",     "fr": "Maison d'hôtes",    "de": "Gästehaus",         "pt": "Casa de hóspedes"},
    "attraction":       {"es": "Atracción turística",  "en": "Tourist attraction", "it": "Attrazione turistica", "fr": "Attraction touristique", "de": "Sehenswürdigkeit", "pt": "Atração turística"},
    "viewpoint":        {"es": "Mirador",              "en": "Viewpoint",         "it": "Punto panoramico",    "fr": "Point de vue",      "de": "Aussichtspunkt",    "pt": "Mirante"},
    "gallery":          {"es": "Galería de arte",      "en": "Art gallery",       "it": "Galleria d'arte",     "fr": "Galerie d'art",     "de": "Kunstgalerie",      "pt": "Galeria de arte"},
    "theatre":          {"es": "Teatro",               "en": "Theatre",           "it": "Teatro",              "fr": "Théâtre",           "de": "Theater",           "pt": "Teatro"},
    "cinema":           {"es": "Cine",                 "en": "Cinema",            "it": "Cinema",              "fr": "Cinéma",            "de": "Kino",              "pt": "Cinema"},
    "pharmacy":         {"es": "Farmacia",             "en": "Pharmacy",          "it": "Farmacia",            "fr": "Pharmacie",         "de": "Apotheke",          "pt": "Farmácia"},
    "bank":             {"es": "Banco",                "en": "Bank",              "it": "Banca",               "fr": "Banque",            "de": "Bank",              "pt": "Banco"},
    "information":      {"es": "Información turística", "en": "Tourist information", "it": "Informazioni turistiche", "fr": "Office de tourisme", "de": "Touristeninformation", "pt": "Informação turística"},
    "monument":         {"es": "Monumento",            "en": "Monument",          "it": "Monumento",           "fr": "Monument",          "de": "Denkmal",           "pt": "Monumento"},
    "ruins":            {"es": "Ruinas",               "en": "Ruins",             "it": "Rovine",              "fr": "Ruines",            "de": "Ruinen",            "pt": "Ruínas"},
    "castle":           {"es": "Fortaleza",            "en": "Fortress",          "it": "Fortezza",            "fr": "Forteresse",        "de": "Festung",           "pt": "Fortaleza"},
    "church":           {"es": "Iglesia",              "en": "Church",            "it": "Chiesa",              "fr": "Église",            "de": "Kirche",            "pt": "Igreja"},
    "place_of_worship": {"es": "Lugar de culto",       "en": "Place of worship",  "it": "Luogo di culto",      "fr": "Lieu de culte",     "de": "Gotteshaus",        "pt": "Local de culto"},
    "memorial":         {"es": "Memorial",             "en": "Memorial",          "it": "Memoriale",           "fr": "Mémorial",          "de": "Gedenkstätte",      "pt": "Memorial"},
}


def tipo_label(tipo: str, idioma: str = IDIOMA_DEFAULT) -> str:
    """Traduce un tipo de lugar de OpenStreetMap (ej. 'restaurant') al idioma indicado."""
    entrada = TIPO_LABELS.get(tipo, {})
    return entrada.get(idioma) or entrada.get(IDIOMA_DEFAULT) or tipo.replace("_", " ").title()
