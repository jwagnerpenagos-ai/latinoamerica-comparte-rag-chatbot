import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag.embeddings import DEFAULT_EMBEDDING_MODEL
from rag.pipeline_groq import GroqRagChatbot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RAG chatbot usando Groq API + retrieval híbrido.")
    parser.add_argument("query", help="Pregunta para el chatbot.")
    parser.add_argument("--chunks-path", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--index-path", type=Path, default=Path("indexes/faiss.index"))
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--min-score", type=float, default=0.20)
    parser.add_argument("--max-context-chars", type=int, default=4500)
    parser.add_argument("--max-tokens", type=int, default=300)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--show-context", action="store_true")
    parser.add_argument("--download-embedding-model", action="store_true")
    return parser.parse_args()


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    args = parse_args()

    chatbot = GroqRagChatbot(
        chunks_path=args.chunks_path,
        index_path=args.index_path,
        embedding_model_name=args.embedding_model,
        local_files_only=not args.download_embedding_model,
    )

    response = chatbot.ask(
        query=args.query,
        top_k=args.top_k,
        min_score=args.min_score,
        max_context_chars=args.max_context_chars,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    if args.show_context:
        print_context(response["context"])

    print("\n" + response["answer"])


def print_context(results: list[dict]) -> None:
    if not results:
        print("No se encontró contexto suficiente.")
        return

    for rank, result in enumerate(results, start=1):
        retrieval_type = result.get("retrieval_type", "unknown")

        print(
            f"\n#{rank} score={result['score']:.4f} "
            f"type={retrieval_type} id={result['id']} source={result['source']}"
        )
        print(result["text"])


if __name__ == "__main__":
    main()