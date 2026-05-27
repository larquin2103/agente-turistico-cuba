#!/bin/bash
# ─────────────────────────────────────────────────────────
#  Agente Turístico Cuba — Script de inicio para demo
#  Uso: bash start.sh
# ─────────────────────────────────────────────────────────
set -e

echo ""
echo "🇨🇺  Agente Turístico Cuba — Iniciando..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verificar .env
if [ ! -f .env ]; then
    echo "⚠️  No se encontró el archivo .env"
    echo "    Copiando plantilla..."
    cp .env.example .env
    echo "    ✏️  Edita .env con tu TELEGRAM_TOKEN y vuelve a ejecutar este script"
    exit 1
fi

# Cargar variables de entorno
set -a
source .env
set +a

OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
DB_PATH="${DB_PATH:-./db}"
API_PORT="${API_PORT:-8000}"

# 2. Verificar Ollama
echo ""
echo "🔍  Verificando Ollama en $OLLAMA_BASE_URL..."
if ! curl -sf "$OLLAMA_BASE_URL/api/version" > /dev/null 2>&1; then
    echo "❌  Ollama no está corriendo."
    echo "    Inicia Ollama con:  ollama serve"
    echo "    Luego asegúrate de tener el modelo:  ollama pull qwen2.5:7b"
    echo "    Y el embedding:  ollama pull nomic-embed-text"
    exit 1
fi
echo "✅  Ollama OK"

# 3. Verificar datos en ChromaDB
echo ""
echo "🗄️   Verificando datos en ChromaDB ($DB_PATH)..."
TOTAL=$(python3 - <<PYEOF 2>/dev/null
import os, chromadb
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

if [ "$TOTAL" -eq "0" ] 2>/dev/null; then
    echo "📥  ChromaDB vacío. Cargando datos turísticos..."
    python3 cargar_datos.py datos/
    echo "✅  Datos cargados"
else
    echo "✅  ChromaDB OK ($TOTAL lugares cargados)"
fi

# 4. Iniciar API FastAPI en background
echo ""
echo "🚀  Iniciando API en el puerto $API_PORT..."
uvicorn api:app --host 0.0.0.0 --port "$API_PORT" --log-level warning &
API_PID=$!

# Esperar a que la API responda (hasta 20 segundos)
echo "⏳  Esperando que la API esté lista..."
for i in $(seq 1 20); do
    if curl -sf "http://localhost:$API_PORT/" > /dev/null 2>&1; then
        echo "✅  API lista en http://localhost:$API_PORT"
        break
    fi
    sleep 1
    if [ "$i" -eq "20" ]; then
        echo "❌  La API no respondió en 20 segundos. Revisa los logs."
        kill $API_PID 2>/dev/null
        exit 1
    fi
done

# 5. Iniciar bot de Telegram
echo ""
echo "🤖  Iniciando bot de Telegram..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "    Bot corriendo. Presiona Ctrl+C para detener."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Capturar Ctrl+C para limpiar procesos correctamente
trap "echo ''; echo '🛑  Deteniendo...'; kill $API_PID 2>/dev/null; exit 0" INT TERM

python3 bot.py

# Cleanup si el bot termina solo
kill $API_PID 2>/dev/null
