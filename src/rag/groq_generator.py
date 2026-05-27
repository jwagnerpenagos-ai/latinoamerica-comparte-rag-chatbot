import os

from groq import Groq

from rag.prompt_builder import FALLBACK_ANSWER


class GroqGenerator:
    """Genera respuestas usando la API de Groq."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise RuntimeError("No encontré GROQ_API_KEY en el archivo .env")

        self.client = Groq(api_key=self.api_key)

    def generate(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 300,
        temperature: float = 0.0,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content.strip()

        if not answer:
            return FALLBACK_ANSWER

        return answer