# Agente Turístico Cuba — Guía de desarrollo

## Estado actual del proyecto

| Componente | Estado | Detalle |
|---|---|---|
| Ollama + qwen2.5:7b | ✅ Funcionando | Puerto 11434 |
| nomic-embed-text | ✅ Funcionando | Embeddings locales |
| LlamaIndex RAG | ✅ Funcionando | similarity_top_k=10 |
| ChromaDB | ✅ Funcionando | 81 lugares de Cuba |
| FastAPI | ✅ Funcionando | Puerto 8000 |
| Bot Telegram | ✅ Funcionando | Long polling |

---

## Estructura del proyecto

```
C:\Users\larquin\agente-turistico\
│
├── api.py                  # API FastAPI — endpoint /chat
├── bot.py                  # Bot Telegram
├── cargar_datos.py         # Cargador de JSONs a ChromaDB
├── test_rag.py             # Pruebas del pipeline RAG
├── diagnostico.py          # Ver documentos indexados en ChromaDB
│
├── datos\                  # JSONs con lugares turísticos
│   ├── Cultura.json
│   ├── havanaGst.json
│   ├── Naturale.json
│   ├── Servicion.json
│   └── transpor.json
│
└── db\                     # ChromaDB persistente (no tocar)
```

---

## Iniciar el entorno de desarrollo

### Paso 1 — Activar el entorno virtual

Siempre activar antes de ejecutar cualquier script:

```powershell
cd C:\Users\larquin\agente-turistico
C:\Users\larquin\agente-turistico\Scripts\activate.ps1
```

El prompt debe mostrar `(agente-turistico)` al inicio.

Si da error de permisos, ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Paso 2 — Verificar que Ollama está corriendo

```powershell
ollama list
```

Debe mostrar `qwen2.5:7b` y `nomic-embed-text` en la lista.

Si Ollama no está corriendo, abrirlo desde el menú de inicio o ejecutar:

```powershell
ollama serve
```

---

### Paso 3 — Levantar la API (ventana 1)

```powershell
cd C:\Users\larquin\agente-turistico
C:\Users\larquin\agente-turistico\Scripts\activate.ps1
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Esperar hasta ver:

```
INFO:     Application startup complete.
```

Verificar que responde:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/" | Select-Object -ExpandProperty Content
```

Debe devolver `{"status":"ok","agente":"turístico","modelo":"qwen2.5:7b"}`.

---

### Paso 4 — Levantar el bot de Telegram (ventana 2)

Abrir una segunda ventana de PowerShell:

```powershell
cd C:\Users\larquin\agente-turistico
C:\Users\larquin\agente-turistico\Scripts\activate.ps1
python bot.py
```

Debe mostrar:

```
Bot corriendo... Ctrl+C para detener
INFO:httpx:HTTP Request: POST https://api.telegram.org/...getMe "HTTP/1.1 200 OK"
```

---

### Paso 5 — Probar el sistema

Probar la API directamente:

```powershell
$body = [System.Text.Encoding]::UTF8.GetBytes('{"texto": "Cual es el mejor restaurante en La Habana", "usuario_id": "test"}')
Invoke-WebRequest -Uri "http://localhost:8000/chat" `
  -Method POST `
  -Headers @{"x-api-key"="turismo-secret-2024"; "Content-Type"="application/json"} `
  -Body $body | Select-Object -ExpandProperty Content
```

O abrir la documentación interactiva en el navegador:

```
http://localhost:8000/docs
```

Probar el bot en Telegram enviando mensajes como:
- "¿Cuál es el mejor restaurante en La Habana?"
- "¿Dónde puedo rentar un auto en Cuba?"
- "¿Qué lugares naturales hay en La Habana?"

---

## Agregar nuevos datos turísticos

### Cargar un archivo nuevo

```powershell
cd C:\Users\larquin\agente-turistico
C:\Users\larquin\agente-turistico\Scripts\activate.ps1
python cargar_datos.py datos\nuevo_archivo.json
```

### Cargar toda la carpeta datos\

```powershell
python cargar_datos.py datos\
```

El sistema detecta duplicados automáticamente por `place_id` — cargar el mismo archivo dos veces no genera duplicados.

Después de cargar datos nuevos, reiniciar la API:

```powershell
# En la ventana 1 — presionar Ctrl+C y volver a ejecutar
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

No es necesario reiniciar el bot.

---

## Diagnosticar problemas

### Ver cuántos documentos hay en ChromaDB y por categoría

```powershell
python diagnostico.py
```

### Ver logs de la API en tiempo real

Los logs aparecen en la ventana donde corre uvicorn. Cada request muestra:

```
INFO:     127.0.0.1:XXXXX - "POST /chat HTTP/1.1" 200 OK
```

Un `500` indica error interno — revisar el traceback en esa ventana.

### Limpiar ChromaDB y reindexar desde cero

Solo hacer esto si los datos están corruptos o mezclados:

```powershell
python -c "
import chromadb
client = chromadb.PersistentClient(path='C:/Users/larquin/agente-turistico/db')
client.delete_collection('lugares_turisticos')
client.create_collection('lugares_turisticos')
print('Coleccion limpiada')
"
python cargar_datos.py datos\
```

---

## Configuración actual

| Parámetro | Valor |
|---|---|
| Modelo LLM | qwen2.5:7b |
| Modelo embeddings | nomic-embed-text |
| similarity_top_k | 10 |
| API Key | turismo-secret-2024 |
| Puerto API | 8000 |
| Puerto Ollama | 11434 |
| ChromaDB path | agente-turistico/db |

---

## Próximos pasos de desarrollo

- [ ] Historial de conversación por usuario
- [ ] Más categorías de datos (hoteles, museos, playas)
- [ ] Soporte multiidioma (inglés, francés)
- [ ] WhatsApp Business API
- [ ] Panel de administración para cargar datos sin línea de comandos
- [ ] Despliegue en servidor para disponibilidad 24/7
- [ ] Langfuse para monitoreo de respuestas del LLM

---

## Dependencias instaladas

```
llama-index
llama-index-llms-ollama
llama-index-embeddings-ollama
llama-index-vector-stores-chroma
chromadb
fastapi
uvicorn
python-telegram-bot
python-dotenv
psycopg2-binary
asyncpg
```

Reinstalar todo desde cero:

```powershell
pip install llama-index llama-index-llms-ollama llama-index-embeddings-ollama llama-index-vector-stores-chroma chromadb fastapi uvicorn python-telegram-bot python-dotenv psycopg2-binary asyncpg
```
