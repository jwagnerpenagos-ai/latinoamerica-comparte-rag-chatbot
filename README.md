# Latinoamérica Comparte RAG Chatbot

Chatbot RAG para responder preguntas sobre Latinoamérica Comparte usando información real de los documentos del proyecto.

El sistema usa una arquitectura con **React + FastAPI + Groq + FAISS + Sentence Transformers**.

---

## Objetivo

Responder preguntas sobre Latinoamérica Comparte, sus programas, líneas principales, impacto, historia y formas de colaboración.

El chatbot debe responder con base en el contexto recuperado. Si no encuentra información suficiente, responde:

```text
No tengo suficiente información para responder esa pregunta con los datos disponibles.
```

---

## Flujo general

```text
Usuario
  -> Frontend React
  -> Backend FastAPI
  -> Retriever híbrido
  -> FAISS + embeddings
  -> Contexto recuperado
  -> Groq
  -> Respuesta
```

---

## Tecnologías

**Backend**

- Python
- FastAPI
- Uvicorn
- FAISS
- Sentence Transformers
- Groq API
- Pydantic
- dotenv

**Frontend**

- React
- Vite
- CSS
- Lucide React

---

## Estructura principal

```text
backend/
  app.py

data/
  raw/
  processed/

frontend/
  public/
  src/
    components/
    hooks/
    styles/
    utils/

indexes/
  faiss.index

scripts/
  build_knowledge_base.py
  chatbot_groq.py
  search_semantic.py

src/rag/
  embeddings.py
  groq_generator.py
  hybrid_retriever.py
  pipeline_groq.py
  prompt_builder.py
  retriever.py
  vector_store.py
```

---

## Instalación backend

Desde la raíz del proyecto:

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
GROQ_API_KEY=tu_api_key_de_groq
GROQ_MODEL=llama-3.1-8b-instant
```

---

## Construir la base de conocimiento

Los documentos fuente van en:

```text
data/raw/
```

Generar chunks, embeddings e índice FAISS:

```bash
python scripts/build_knowledge_base.py
```

Archivos generados:

```text
data/processed/chunks.jsonl
data/processed/embeddings.npy
indexes/faiss.index
```

---

## Probar retrieval

```bash
python scripts/search_semantic.py "Qué es DESKUBRE?"
```

---

## Probar chatbot por consola

```bash
python scripts/chatbot_groq.py "Qué es Latinoamérica Comparte?"
```

Con contexto recuperado:

```bash
python scripts/chatbot_groq.py "Qué es ESTRUCTURA?" --show-context
```

---

## Ejecutar backend

Desde la raíz:

```bash
uvicorn backend.app:app --reload
```

Backend disponible en:

```text
http://localhost:8000
```

---

## Ejecutar frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en:

```text
http://localhost:5173
```

---

## Comportamiento esperado

El asistente debe:

- Responder en español.
- Usar solo la información recuperada.
- No inventar datos.
- Usar fallback si no hay contexto suficiente.
- Recomendar **DESKUBRE** para ideas iniciales de emprendimiento.
- Recomendar **ESTRUCTURA** para emprendimientos en marcha o ideas más avanzadas.
- Orientar sobre Comparte Academia, Comparte Liderazgo y Comparte Talento.
- Diferenciar entre usuarios que buscan ayuda para emprender y usuarios que quieren colaborar con la organización.

---

## Ejemplos de preguntas

```text
¿Qué es Latinoamérica Comparte?
¿En qué países están?
Tengo una idea para un emprendimiento, ¿me pueden ayudar?
¿Qué es DESKUBRE?
Ya tengo un emprendimiento, pero está desordenado. ¿Qué me sirve?
Necesito un conferencista para una charla en mi empresa.
¿Cómo puedo colaborar con ustedes?
¿A cuántas personas han acompañado?
```

---

## Estado actual

El proyecto funciona con:

```text
React + FastAPI + Groq + FAISS + Sentence Transformers
```

La versión anterior basada en Streamlit y Qwen fue retirada para mantener una arquitectura más clara y moderna.
