# Video Promocional · SaaS Agente IA con RAG

Video de 2:30 min generado con [Remotion](https://www.remotion.dev/) basado en el guión `videopromosaasrag.jsx`. Renderiza en dos formatos (horizontal 1920×1080 y vertical 1080×1920) directamente desde código React/TypeScript.

## Estructura

```
remotion-video/
├── package.json
├── remotion.config.ts
├── tsconfig.json
└── src/
    ├── index.ts                # Entry point — registerRoot
    ├── Root.tsx                # Registra las composiciones
    ├── Video.tsx               # Orquestador (Series de escenas)
    ├── fonts.ts                # Carga de Google Fonts (Inter / Playfair / JetBrains)
    ├── data/scenes.ts          # Datos de las 17 escenas (del guión original)
    └── components/
        ├── SceneRenderer.tsx   # Layout común: badge, título, narración, dato/gancho
        ├── ProgressBar.tsx     # Barra de progreso multicolor inferior
        └── visuals/            # Visual específico por escena
            ├── SceneVisual.tsx     # Router por scene.id
            ├── ProblemPhone.tsx    # Esc 1
            ├── LostMoney.tsx       # Esc 2
            ├── LogoReveal.tsx      # Esc 3
            ├── HowItWorks.tsx      # Esc 4
            ├── WhatsAppChat.tsx    # Esc 5, 9, 10
            ├── BeforeAfter.tsx     # Esc 6
            ├── TiredVsBot.tsx      # Esc 7
            ├── Dashboard.tsx       # Esc 8, 12
            ├── TravelTimeline.tsx  # Esc 11
            ├── PlatformCompare.tsx # Esc 13
            ├── GroundedBot.tsx     # Esc 14
            ├── ScaleViz.tsx        # Esc 15
            ├── BusinessCarousel.tsx# Esc 16
            └── CallToAction.tsx    # Esc 17
```

## Composiciones registradas

| ID | Resolución | Uso |
|---|---|---|
| `PromoVideo` | 1920×1080 (16:9) | YouTube, Web, LinkedIn, landing |
| `PromoVideoVertical` | 1080×1920 (9:16) | Instagram Reels, TikTok, Stories |

Duración total: **150 s** (4500 frames @ 30 fps).

## Uso

### 1. Instalar dependencias

```bash
cd remotion-video
npm install
```

### 2. Abrir Remotion Studio (preview interactivo)

```bash
npm run dev
```

Abre `http://localhost:3000` — puedes navegar escena por escena, ver la timeline y ajustar en vivo.

### 3. Renderizar a MP4

```bash
# Versión horizontal (YouTube/Web)
npm run build

# Versión vertical (Reels/TikTok)
npm run build:reels

# Las dos
npm run build:all
```

Los archivos se guardan en `out/promo-video.mp4` y `out/promo-reels.mp4`.

### 4. Generar poster (frame estático)

```bash
npm run still
```

## Personalización rápida

- **Cambiar textos / narraciones**: editar `src/data/scenes.ts`.
- **Cambiar colores por acto**: campos `color` y `bg` en cada escena, además del map `actMeta`.
- **Cambiar duración de una escena**: campo `duration` (en segundos).
- **Agregar voz en off**: añadir `<Audio src={...} />` dentro de cada `Series.Sequence` en `Video.tsx` con voz generada por ElevenLabs.
- **Agregar música de fondo**: `<Audio src={staticFile('musica.mp3')} volume={0.2} />` en `PromoVideo`.

## Notas de producción

- El diseño usa **motion graphics tipográfico** + mockups de WhatsApp/Telegram. No requiere footage real.
- Las paletas por escena replican el guión original (rojo problema, azul solución, rosa dental, etc.).
- La barra inferior es un gradiente que recorre todos los actos para dar continuidad visual.
- Para añadir voz en off generada con IA (ElevenLabs), guardar los archivos en `public/voz/escena-XX.mp3` y agregar `<Audio>` en cada secuencia.

## Stack

- Remotion 4.x
- React 18 + TypeScript
- `@remotion/google-fonts` para Inter, Playfair Display, JetBrains Mono
- Sin assets externos — todo es código (SVG + CSS + animaciones de Remotion)
