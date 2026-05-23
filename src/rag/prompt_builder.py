FALLBACK_ANSWER = "No tengo suficiente información para responder esa pregunta con los datos disponibles."


class PromptBuilder:
    """Construye los mensajes para el modelo de lenguaje."""

    def build_messages(self, query: str, context: str) -> list[dict[str, str]]:
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, context)

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def _build_system_prompt(self) -> str:
        return f"""
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
10. Si el contexto no contiene información suficiente, responde exactamente:
"{FALLBACK_ANSWER}"

FORMATO:
- Responde de forma clara y breve.
- Máximo 4 frases.
- No menciones “según el contexto” salvo que sea necesario.
""".strip()

    def _build_user_prompt(self, query: str, context: str) -> str:
        return f"""
CONTEXTO RECUPERADO:
{context}

PREGUNTA DEL USUARIO:
{query}

INSTRUCCIÓN:
Primero identifica si el contexto contiene información relacionada con la pregunta.
Si la pregunta contiene una suposición falsa, corrígela con el dato correcto del contexto.
Solo usa fallback si el contexto no contiene información relacionada.

RESPUESTA:
""".strip()