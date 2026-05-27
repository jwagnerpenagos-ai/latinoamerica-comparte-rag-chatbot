from pathlib import Path
import sys

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

load_dotenv(PROJECT_ROOT / ".env")

from rag.embeddings import DEFAULT_EMBEDDING_MODEL
from rag.pipeline_groq import GroqRagChatbot

from ui.components import render_chat, render_landing
from ui.state import ensure_state
from ui.styles import apply_styles


TOP_K = 6
MIN_SCORE = 0.20
MAX_TOKENS = 300
TEMPERATURE = 0.0
MAX_CONTEXT_CHARS = 4500


st.set_page_config(
    page_title="Latinoamérica Comparte",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(show_spinner="Preparando el asistente de Latinoamérica Comparte...")
def load_chatbot() -> GroqRagChatbot:
    return GroqRagChatbot(
        chunks_path=PROJECT_ROOT / "data/processed/chunks.jsonl",
        index_path=PROJECT_ROOT / "indexes/faiss.index",
        embedding_model_name=DEFAULT_EMBEDDING_MODEL,
        local_files_only=True,
    )


def ask_question(question: str) -> str:
    chatbot = load_chatbot()

    response = chatbot.ask(
        query=question,
        top_k=TOP_K,
        min_score=MIN_SCORE,
        max_context_chars=MAX_CONTEXT_CHARS,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    return response["answer"]


def main() -> None:
    ensure_state()
    apply_styles()
    render_landing()
    render_chat(ask_question)


if __name__ == "__main__":
    main()