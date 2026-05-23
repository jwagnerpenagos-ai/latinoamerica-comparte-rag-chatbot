import argparse
import os
import sys
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag.embeddings import DEFAULT_EMBEDDING_MODEL, create_embeddings, load_embedding_model
from rag.retriever import load_chunks
from rag.vector_store import load_faiss_index, search_index


FALLBACK_ANSWER = "No tengo suficiente información para responder esa pregunta con los datos disponibles."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RAG chatbot usando Groq API + FAISS local.")
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


def retrieve_context(query: str, args: argparse.Namespace) -> list[dict]:
    chunks = load_chunks(args.chunks_path)
    index = load_faiss_index(args.index_path)

    embedding_model = load_embedding_model(
        args.embedding_model,
        local_files_only=not args.download_embedding_model,
    )

    semantic_results = semantic_retrieve(
        query=query,
        chunks=chunks,
        index=index,
        embedding_model=embedding_model,
        top_k=args.top_k,
        min_score=args.min_score,
    )

    keyword_results = keyword_retrieve(
        query=query,
        chunks=chunks,
        limit=args.top_k,
    )

    return merge_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=args.top_k,
    )


def semantic_retrieve(
    query: str,
    chunks: list[dict],
    index,
    embedding_model,
    top_k: int,
    min_score: float,
) -> list[dict]:
    query_embedding = create_embeddings([query], embedding_model)
    scores, indexes = search_index(index, query_embedding, top_k)

    results = []

    for score, chunk_index in zip(scores, indexes):
        if chunk_index == -1:
            continue

        score = float(score)

        if score < min_score:
            continue

        chunk = chunks[chunk_index]

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


def keyword_retrieve(query: str, chunks: list[dict], limit: int = 6) -> list[dict]:
    terms = extract_query_terms(query)

    if not terms:
        return []

    scored_results = []

    for chunk_index, chunk in enumerate(chunks):
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


def calculate_keyword_score(
    terms: list[str],
    normalized_text: str,
    normalized_source: str,
) -> int:
    score = 0

    for term in terms:
        if term in normalized_text:
            score += 1

    # Priorización por archivo específico. Esto no responde nada;
    # solo mejora la recuperación del documento correcto.
    if "deskubre" in terms or "descubre" in terms:
        if "07_deskubre" in normalized_source:
            score += 6
        if "01_comparte_academia" in normalized_source:
            score += 2

    if "estructura" in terms:
        if "08_estructura" in normalized_source:
            score += 6
        if "01_comparte_academia" in normalized_source:
            score += 2

    if "comparte academia" in terms:
        if "01_comparte_academia" in normalized_source:
            score += 4
        if "00_base_latinoamerica" in normalized_source:
            score += 2

    if "comparte liderazgo" in terms or "nodus" in terms or "liderazgo" in terms:
        if "02_comparte_liderazgo_talento" in normalized_source:
            score += 4

    if "comparte talento" in terms or "top speakers" in terms or "speakers" in terms:
        if "02_comparte_liderazgo_talento" in normalized_source:
            score += 4

    if "pobreza oculta" in terms or "pobreza vergonzante" in terms:
        if "03_publicos_pobreza_oculta_historia" in normalized_source:
            score += 4

    if "impacto" in terms or "contacto" in terms or "colaboracion" in terms:
        if "04_impacto_colaboracion_contacto" in normalized_source:
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

    if any(word in normalized_query for word in ["dura", "duracion", "anos", "año", "anos", "mes", "meses"]):
        terms.append("duracion")

    if any(word in normalized_query for word in ["emprendimiento", "emprender", "emprendedor", "negocio", "idea"]):
        terms.append("emprendimiento")

    if any(word in normalized_query for word in ["speaker", "speakers", "conferencista", "evento", "charla"]):
        terms.append("speakers")

    if any(word in normalized_query for word in ["liderazgo", "lideres", "lider", "colaboradores", "empresa"]):
        terms.append("liderazgo")

    if any(word in normalized_query for word in ["impacto", "personas", "familias", "empresas", "mentores"]):
        terms.append("impacto")

    if any(word in normalized_query for word in ["contacto", "correo", "telefono", "comunicar", "ayudar", "colaborar"]):
        terms.append("contacto")
        terms.append("colaboracion")

    return list(dict.fromkeys(terms))


def merge_results(
    keyword_results: list[dict],
    semantic_results: list[dict],
    limit: int,
) -> list[dict]:
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


def build_context(results: list[dict], max_context_chars: int) -> str:
    blocks = []
    used_chars = 0

    for i, result in enumerate(results, start=1):
        retrieval_type = result.get("retrieval_type", "unknown")

        block = (
            f"[Fuente {i} | score={result['score']:.4f} | tipo={retrieval_type} | archivo={result['source']}]\n"
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


def build_messages(query: str, context: str) -> list[dict]:
    system_prompt = f"""
Eres el asistente virtual oficial de Latinoamérica Comparte.

REGLAS OBLIGATORIAS:
1. Responde siempre en español.
2. Usa únicamente la información del contexto recuperado.
3. No uses conocimiento externo.
4. No des consejos generales.
5. No inventes precios, fechas, sedes, aliados, programas ni enlaces.
6. El fallback solo se usa cuando el contexto no contiene ninguna información relacionada con la pregunta.
7. Si el usuario hace una afirmación falsa, incorrecta o contradictoria, y el contexto contiene el dato correcto, corrige la afirmación usando ese dato.
8. Si el contexto contiene información relacionada con la pregunta, responde con esa información aunque la pregunta del usuario esté formulada como una suposición incorrecta.
9. No mezcles información de fuentes distintas si no corresponde a la pregunta.

FORMATO:
- Responde de forma clara y breve.
- Máximo 4 frases.
- No menciones “según el contexto” salvo que sea necesario.
""".strip()

    user_prompt = f"""
CONTEXTO RECUPERADO:
{context}

PREGUNTA DEL USUARIO:
{query}

INSTRUCCIÓN:
Primero identifica si el contexto contiene información relacionada con la pregunta.
Si la pregunta contiene una suposición falsa, corrígela con el dato correcto del contexto.
Solo usa fallback si el contexto no contiene información relacionada.

RESPUESTA:

RESPUESTA:
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def generate_with_groq(query: str, context: str, max_tokens: int, temperature: float) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        raise RuntimeError("No encontré GROQ_API_KEY en el archivo .env")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=build_messages(query, context),
        temperature=temperature,
        max_tokens=max_tokens,
    )

    answer = response.choices[0].message.content.strip()

    if not answer:
        return FALLBACK_ANSWER

    return answer


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


def normalize_text(text: str) -> str:
    text = text.lower()

    text = "".join(
        character
        for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    )

    return text


def main() -> None:
    load_dotenv()
    args = parse_args()

    results = retrieve_context(args.query, args)

    if args.show_context:
        print_context(results)

    if not results:
        print(FALLBACK_ANSWER)
        return

    context = build_context(results, args.max_context_chars)

    answer = generate_with_groq(
        query=args.query,
        context=context,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    print("\n" + answer)


if __name__ == "__main__":
    main()