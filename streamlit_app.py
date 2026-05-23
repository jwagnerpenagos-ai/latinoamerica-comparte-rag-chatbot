from pathlib import Path
import sys
from types import SimpleNamespace

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

load_dotenv(PROJECT_ROOT / ".env")

from rag.embeddings import DEFAULT_EMBEDDING_MODEL

from scripts.chatbot_groq import (
    retrieve_context,
    build_context,
    generate_with_groq,
    FALLBACK_ANSWER,
)


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

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
    .main .block-container {
        max-width: 1180px;
        padding: 1.4rem 2rem 2.2rem;
    }
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 0.9rem;
        margin-bottom: 2.2rem;
    }
    .brand {
        font-size: 1.05rem;
        font-weight: 800;
        color: #111827;
    }
    .nav-note {
        color: #6b7280;
        font-size: 0.92rem;
    }
    .hero {
        min-height: 58vh;
        display: grid;
        align-items: center;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 2.6rem;
    }
    .eyebrow {
        color: #0f766e;
        font-weight: 750;
        margin-bottom: 0.7rem;
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0;
    }
    .hero h1 {
        font-size: clamp(2.1rem, 5vw, 4.8rem);
        line-height: 1.02;
        margin: 0 0 1rem;
        color: #111827;
        letter-spacing: 0;
        max-width: 860px;
    }
    .hero p {
        font-size: 1.12rem;
        color: #4b5563;
        max-width: 680px;
        line-height: 1.65;
        margin-bottom: 1.4rem;
    }
    .trust-row {
        display: flex;
        gap: 1.4rem;
        flex-wrap: wrap;
        margin-top: 1.6rem;
        color: #374151;
    }
    .trust-item strong {
        display: block;
        font-size: 1.35rem;
        color: #111827;
    }
    .chat-shell {
        border: 1px solid #d1d5db;
        background: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 18px 45px rgba(17, 24, 39, 0.12);
        margin-top: 1rem;
    }
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 0.8rem;
        margin-bottom: 0.9rem;
    }
    .chat-title {
        font-weight: 800;
        color: #111827;
    }
    .chat-status {
        color: #0f766e;
        font-size: 0.88rem;
        font-weight: 650;
    }
    .hint {
        color: #6b7280;
        font-size: 0.92rem;
        margin-top: 0.6rem;
    }
    .stButton > button {
        border-radius: 999px;
        border: 1px solid #0f766e;
        background: #0f766e;
        color: white;
        font-weight: 700;
        min-height: 2.7rem;
    }
    .stButton > button:hover {
        border: 1px solid #115e59;
        background: #115e59;
        color: white;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 8px;
    }
    @media (max-width: 760px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .topbar {
            align-items: flex-start;
            gap: 0.5rem;
            flex-direction: column;
        }
        .hero {
            min-height: 52vh;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    _ensure_state()
    _render_landing()

    if st.session_state.chat_open:
        _render_chat()


def _render_landing() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">Latinoamérica Comparte</div>
            <div class="nav-note">Emprendimiento, liderazgo, talento y reconstrucción productiva</div>
        </div>
        <section class="hero">
            <div>
                <div class="eyebrow">Chatbot inteligente con RAG</div>
                <h1>Respuestas claras sobre Latinoamérica Comparte, en segundos.</h1>
                <p>
                    Consulta información sobre Comparte Academia, DESKUBRE, ESTRUCTURA,
                    Comparte Liderazgo, Comparte Talento, historia, impacto y formas de colaboración.
                    El asistente recupera contexto desde la base documental antes de responder.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    action_col, example_col_1, example_col_2, example_col_3 = st.columns([1.25, 1, 1, 1])

    with action_col:
        if st.button("💬 Abrir chat", use_container_width=True):
            st.session_state.chat_open = True
            st.rerun()

    with example_col_1:
        if st.button("Comparte Academia", use_container_width=True):
            _open_with_question("¿Qué es Comparte Academia?")

    with example_col_2:
        if st.button("Impacto", use_container_width=True):
            _open_with_question("¿Cuál ha sido el impacto de Latinoamérica Comparte?")

    with example_col_3:
        if st.button("Historia", use_container_width=True):
            _open_with_question("¿Cómo nació Colombia Comparte?")

    st.markdown(
        """
        <div class="trust-row">
            <div class="trust-item"><strong>RAG</strong>Busca primero en documentos reales.</div>
            <div class="trust-item"><strong>FAISS</strong>Recupera contexto por similitud.</div>
            <div class="trust-item"><strong>Groq + Llama</strong>Redacta respuestas naturales.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_chat() -> None:
    st.markdown(
        """
        <div class="chat-shell">
            <div class="chat-header">
                <div class="chat-title">Asistente Latinoamérica Comparte</div>
                <div class="chat-status">Disponible</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_area = st.container()

    with chat_area:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    pending_question = st.session_state.pop("pending_question", None)
    typed_question = st.chat_input("Pregúntame sobre Latinoamérica Comparte")

    question = pending_question or typed_question

    if not question:
        st.markdown(
            '<div class="hint">Puedes preguntar por DESKUBRE, ESTRUCTURA, Comparte Liderazgo, Comparte Talento, impacto, historia o formas de colaboración.</div>',
            unsafe_allow_html=True,
        )
        return

    _answer_question(question)


def ask_with_groq(question: str) -> str:
    args = SimpleNamespace(
        chunks_path=PROJECT_ROOT / "data/processed/chunks.jsonl",
        index_path=PROJECT_ROOT / "indexes/faiss.index",
        embedding_model=DEFAULT_EMBEDDING_MODEL,
        top_k=TOP_K,
        min_score=MIN_SCORE,
        max_context_chars=MAX_CONTEXT_CHARS,
        download_embedding_model=False,
    )

    results = retrieve_context(question, args)

    if not results:
        return FALLBACK_ANSWER

    context = build_context(results, MAX_CONTEXT_CHARS)

    return generate_with_groq(
        query=question,
        context=context,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )


def _answer_question(question: str) -> None:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de conocimiento..."):
            try:
                answer = ask_with_groq(question)
            except Exception as error:
                answer = (
                    "Ocurrió un error al consultar el modelo. "
                    "Verifica que GROQ_API_KEY esté configurada en el archivo .env "
                    f"y que tengas conexión a internet.\n\nDetalle técnico: `{error}`"
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


def _ensure_state() -> None:
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hola, soy el asistente virtual de Latinoamérica Comparte. "
                    "Puedo ayudarte con información sobre Comparte Academia, DESKUBRE, "
                    "ESTRUCTURA, Comparte Liderazgo, Comparte Talento, impacto, historia "
                    "y formas de colaboración."
                ),
            }
        ]


def _open_with_question(question: str) -> None:
    st.session_state.chat_open = True
    st.session_state.pending_question = question
    st.rerun()


if __name__ == "__main__":
    main()