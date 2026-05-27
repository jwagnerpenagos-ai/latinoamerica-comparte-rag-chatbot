import unicodedata
from pathlib import Path
from typing import Any

from rag.embeddings import create_embeddings, load_embedding_model
from rag.retriever import load_chunks
from rag.vector_store import load_faiss_index, search_index


class HybridRetriever:
    """
    Recupera contexto combinando:
    1. Búsqueda semántica con embeddings + FAISS.
    2. Búsqueda por palabras clave para entidades importantes.
    """

    def __init__(
        self,
        chunks_path: Path,
        index_path: Path,
        embedding_model_name: str,
        local_files_only: bool = True,
    ) -> None:
        self.chunks = load_chunks(chunks_path)
        self.index = load_faiss_index(index_path)
        self.embedding_model = load_embedding_model(
            embedding_model_name,
            local_files_only=local_files_only,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        min_score: float = 0.20,
    ) -> list[dict[str, Any]]:
        semantic_results = self._semantic_retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        keyword_results = self._keyword_retrieve(
            query=query,
            limit=top_k,
        )

        return self._merge_results(
            keyword_results=keyword_results,
            semantic_results=semantic_results,
            limit=top_k,
        )

    def _semantic_retrieve(
        self,
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[dict[str, Any]]:
        query_embedding = create_embeddings([query], self.embedding_model)
        scores, indexes = search_index(self.index, query_embedding, top_k)

        results = []

        for score, chunk_index in zip(scores, indexes):
            if chunk_index == -1:
                continue

            score = float(score)

            if score < min_score:
                continue

            chunk = self.chunks[chunk_index]

            results.append(
                {
                    "score": score,
                    "id": chunk.get("id", f"chunk-{chunk_index}"),
                    "source": chunk.get("source", "unknown"),
                    "text": chunk.get("text", ""),
                    "retrieval_type": "semantic",
                }
            )

        return results

    def _keyword_retrieve(
        self,
        query: str,
        limit: int = 6,
    ) -> list[dict[str, Any]]:
        terms = extract_query_terms(query)

        if not terms:
            return []

        scored_results = []

        for chunk_index, chunk in enumerate(self.chunks):
            text = chunk.get("text", "")
            source = chunk.get("source", "unknown")

            normalized_text = normalize_text(text)
            normalized_source = normalize_text(source)

            keyword_score = calculate_keyword_score(
                terms=terms,
                normalized_text=normalized_text,
                normalized_source=normalized_source,
            )

            if keyword_score <= 0:
                continue

            scored_results.append(
                {
                    "score": min(0.99, 0.70 + keyword_score * 0.03),
                    "id": chunk.get("id", f"chunk-{chunk_index}"),
                    "source": source,
                    "text": text,
                    "retrieval_type": "keyword",
                }
            )

        scored_results.sort(key=lambda item: item["score"], reverse=True)
        return scored_results[:limit]

    @staticmethod
    def _merge_results(
        keyword_results: list[dict[str, Any]],
        semantic_results: list[dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        merged = []
        seen_ids = set()

        for result in keyword_results + semantic_results:
            result_id = result["id"]

            if result_id in seen_ids:
                continue

            merged.append(result)
            seen_ids.add(result_id)

            if len(merged) >= limit:
                break

        return merged


def build_context(
    results: list[dict[str, Any]],
    max_context_chars: int = 4500,
) -> str:
    blocks = []
    used_chars = 0

    for index, result in enumerate(results, start=1):
        retrieval_type = result.get("retrieval_type", "unknown")

        block = (
            f"[Fuente {index} | score={result['score']:.4f} | "
            f"tipo={retrieval_type} | archivo={result['source']}]\n"
            f"{result['text'].strip()}"
        )

        if used_chars + len(block) > max_context_chars:
            remaining = max_context_chars - used_chars

            if remaining > 500:
                block = block[:remaining].rsplit(" ", 1)[0]
                blocks.append(block)

            break

        blocks.append(block)
        used_chars += len(block)

    return "\n\n---\n\n".join(blocks)


def calculate_keyword_score(
    terms: list[str],
    normalized_text: str,
    normalized_source: str,
) -> int:
    score = 0

    for term in terms:
        if term in normalized_text:
            score += 1

    if "idea_emprendimiento" in terms:
        if "07_deskubre" in normalized_source:
            score += 8
        if "01_comparte_academia" in normalized_source:
            score += 6
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 5

    if "emprendimiento" in terms:
        if "01_comparte_academia" in normalized_source:
            score += 4
        if "07_deskubre" in normalized_source:
            score += 4
        if "08_estructura" in normalized_source:
            score += 3
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "deskubre" in terms or "descubre" in terms:
        if "07_deskubre" in normalized_source:
            score += 8
        if "01_comparte_academia" in normalized_source:
            score += 3
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "estructura" in terms:
        if "08_estructura" in normalized_source:
            score += 8
        if "01_comparte_academia" in normalized_source:
            score += 3
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "comparte academia" in terms:
        if "01_comparte_academia" in normalized_source:
            score += 6
        if "07_deskubre" in normalized_source:
            score += 3
        if "08_estructura" in normalized_source:
            score += 3
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 4
        if "00_base_latinoamerica" in normalized_source:
            score += 2

    if "comparte liderazgo" in terms or "nodus" in terms or "liderazgo" in terms:
        if "02_comparte_liderazgo_talento" in normalized_source:
            score += 5
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "comparte talento" in terms or "top speakers" in terms or "speakers" in terms:
        if "02_comparte_liderazgo_talento" in normalized_source:
            score += 5
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "pobreza_oculta" in terms or "pobreza vergonzante" in terms:
        if "03_publicos_pobreza_oculta_historia" in normalized_source:
            score += 5
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "presencia_regional" in terms:
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 6
        if "00_base_latinoamerica" in normalized_source:
            score += 3

    if "impacto" in terms:
        if "04_impacto_colaboracion_contacto" in normalized_source:
            score += 5
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "contacto" in terms:
        if "04_impacto_colaboracion_contacto" in normalized_source:
            score += 5
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 3

    if "colaboracion" in terms:
        if "04_impacto_colaboracion_contacto" in normalized_source:
            score += 6
        if "05_faq_preguntas_respuestas" in normalized_source:
            score += 4

    return score


def extract_query_terms(query: str) -> list[str]:
    normalized_query = normalize_text(query)

    controlled_terms = [
        "deskubre",
        "descubre",
        "estructura",
        "edifica",
        "nodus",
        "top speakers",
        "comparte academia",
        "comparte liderazgo",
        "comparte talento",
        "latinoamerica comparte",
        "colombia comparte",
        "pobreza oculta",
        "pobreza vergonzante",
    ]

    terms = []

    for term in controlled_terms:
        if term in normalized_query:
            terms.append(term)

    if any(
        word in normalized_query
        for word in [
            "pais",
            "paises",
            "presencia",
            "presentes",
            "colombia",
            "ecuador",
            "chile",
            "argentina",
            "latinoamerica",
        ]
    ):
        terms.append("presencia_regional")

    if any(
        word in normalized_query
        for word in [
            "dura",
            "duracion",
            "anos",
            "año",
            "mes",
            "meses",
        ]
    ):
        terms.append("duracion")

    if any(
        word in normalized_query
        for word in [
            "emprendimiento",
            "emprender",
            "emprendedor",
            "emprendedora",
            "negocio",
            "idea",
            "proyecto",
        ]
    ):
        terms.append("emprendimiento")

    if "idea" in normalized_query and any(
        word in normalized_query
        for word in [
            "emprendimiento",
            "emprender",
            "negocio",
            "proyecto",
        ]
    ):
        terms.append("idea_emprendimiento")

    if any(
        phrase in normalized_query
        for phrase in [
            "quiero emprender",
            "quiero empezar",
            "empezar a emprender",
            "emprender desde cero",
            "tengo una idea",
            "idea de negocio",
            "idea para un emprendimiento",
            "llevarla a cabo",
            "llevar a cabo una idea",
        ]
    ):
        terms.append("idea_emprendimiento")

    if any(
        word in normalized_query
        for word in [
            "speaker",
            "speakers",
            "conferencista",
            "conferencia",
            "evento",
            "charla",
        ]
    ):
        terms.append("speakers")

    if any(
        word in normalized_query
        for word in [
            "liderazgo",
            "lideres",
            "lider",
            "colaboradores",
            "empresa",
            "empresas",
            "cultura",
            "bienestar",
        ]
    ):
        terms.append("liderazgo")

    if any(
        word in normalized_query
        for word in [
            "impacto",
            "personas",
            "familias",
            "mentores",
            "resultados",
            "acompanado",
            "acompañando",
            "acompañado",
        ]
    ):
        terms.append("impacto")

    if any(
        word in normalized_query
        for word in [
            "contacto",
            "correo",
            "telefono",
            "teléfono",
            "comunicar",
            "email",
            "asesor",
            "asesora",
            "pagina",
            "página",
            "web",
        ]
    ):
        terms.append("contacto")

    if any(
        phrase in normalized_query
        for phrase in [
            "donar",
            "donacion",
            "donaciones",
            "voluntario",
            "voluntariado",
            "aliado",
            "aliados",
            "alianza",
            "alianzas",
            "colaborar",
            "apoyar a la organizacion",
            "apoyar a la organización",
            "apoyarlos",
            "como puedo apoyarlos",
            "como puedo ayudarles",
            "como puedo colaborar",
        ]
    ):
        terms.append("colaboracion")

    return list(dict.fromkeys(terms))


def normalize_text(text: str) -> str:
    text = text.lower()

    return "".join(
        character
        for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    )