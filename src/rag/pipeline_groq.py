from pathlib import Path
from typing import Any

from rag.embeddings import DEFAULT_EMBEDDING_MODEL
from rag.groq_generator import GroqGenerator
from rag.hybrid_retriever import HybridRetriever, build_context
from rag.prompt_builder import FALLBACK_ANSWER, PromptBuilder


class GroqRagChatbot:
    """Pipeline completo: retrieval híbrido + prompt + Groq/Llama."""

    def __init__(
        self,
        chunks_path: Path = Path("data/processed/chunks.jsonl"),
        index_path: Path = Path("indexes/faiss.index"),
        embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
        local_files_only: bool = True,
        groq_model: str | None = None,
    ) -> None:
        self.retriever = HybridRetriever(
            chunks_path=chunks_path,
            index_path=index_path,
            embedding_model_name=embedding_model_name,
            local_files_only=local_files_only,
        )

        self.prompt_builder = PromptBuilder()
        self.generator = GroqGenerator(model=groq_model)

    def ask(
        self,
        query: str,
        top_k: int = 6,
        min_score: float = 0.20,
        max_context_chars: int = 4500,
        max_tokens: int = 300,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        if not results:
            return {
                "answer": FALLBACK_ANSWER,
                "context": [],
            }

        context = build_context(
            results=results,
            max_context_chars=max_context_chars,
        )

        messages = self.prompt_builder.build_messages(
            query=query,
            context=context,
        )

        answer = self.generator.generate(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return {
            "answer": answer,
            "context": results,
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        min_score: float = 0.20,
    ) -> list[dict[str, Any]]:
        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )