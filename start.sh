#!/bin/bash
# ─────────────────────────────────────────────────────────
#  Agente Turístico Cuba — Script de inicio
#  Uso: bash start.sh
# ─────────────────────────────────────────────────────────
set -e

echo ""
echo "🇨🇺  Agente Turístico Cuba — Iniciando..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verificar .env
if [ ! -f .env ]; then
    echo "⚠️  No se encontró .env — copiando plantilla..."
    cp .env.example .env
    echo "✏️  Edita .env con tu TELEGRAM_TOKEN y GROQ_API_KEY, luego vuelve a ejecutar"
    exit 1
fi

set -a; source .env; set +a

DB_PATH="${DB_PATH:-./db}"
API_PORT="${API_PORT:-8000}"

# 2. Verificar GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    echo "❌  GROQ_API_KEY no configurado en .env"
    echo "    Regístrate gratis en https://console.groq.com y pega tu API key"
    exit 1
fi
echo "✅  Groq API key OK"

# 3. Verificar/cargar datos en ChromaDB
echo ""
echo "🗄️   Verificando ChromaDB ($DB_PATH)..."

TOTAL=$(python3 - <<'PYEOF' 2>/dev/null
import os, sys, chromadb
from dotenv import load_dotenv
load_dotenv()
db = os.getenv("DB_PATH", "./db")
try:
    c = chromadb.PersistentClient(path=db)
    col = c.get_or_create_collection("lugares_turisticos")
    print(col.count())
except Exception:
    print(0)
PYEOF
)

if [ "${TOTAL:-0}" -eq "0" ] 2>/dev/null; then
    echo "📥  ChromaDB vacío. Indexando datos turísticos (primera vez puede tardar 1-2 min)..."
    python3 cargar_datos.py datos/
    echo "✅  Datos indexados"
else
    echo "✅  ChromaDB OK ($TOTAL lugares)"
fi

# 4. Iniciar API en background
echo ""
echo "🚀  Iniciando API (puerto $API_PORT)..."
uvicorn api:app --host 0.0.0.0 --port "$API_PORT" --log-level warning &
API_PID=$!

echo "⏳  Esperando que la API esté lista..."
for i in $(seq 1 25); do
    if curl -sf "http://localhost:$API_PORT/" > /dev/null 2>&1; then
        echo "✅  API lista → http://localhost:$API_PORT"
        break
    fi
    sleep 1
    if [ "$i" -eq "25" ]; then
        echo "❌  La API no respondió. Revisa los logs arriba."
        kill $API_PID 2>/dev/null
        exit 1
    fi
done

# 5. Iniciar bot
echo ""
echo "🤖  Iniciando bot de Telegram..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "    ✅ Bot corriendo. Presiona Ctrl+C para detener."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

trap "echo ''; echo '🛑 Deteniendo...'; kill $API_PID 2>/dev/null; exit 0" INT TERM

python3 bot.py

kill $API_PID 2>/dev/null
