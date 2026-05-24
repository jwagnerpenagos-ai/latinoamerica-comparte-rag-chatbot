from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from rag.pipeline_groq import GroqRagChatbot


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


app = FastAPI(
    title="Latinoamérica Comparte RAG API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


chatbot = GroqRagChatbot(
    chunks_path=ROOT_DIR / "data" / "processed" / "chunks.jsonl",
    index_path=ROOT_DIR / "indexes" / "faiss.index",
    local_files_only=True,
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Latinoamérica Comparte RAG API is running",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()

    if not question:
        return ChatResponse(
            answer="Por favor escribe una pregunta para poder ayudarte."
        )

    try:
        result: dict[str, Any] = chatbot.ask(question)
        answer = result.get("answer", "No se pudo generar una respuesta.")
        return ChatResponse(answer=answer)

    except Exception as error:
        return ChatResponse(
            answer=(
                "Ocurrió un error al consultar el asistente. "
                f"Detalle técnico: {error}"
            )
        )