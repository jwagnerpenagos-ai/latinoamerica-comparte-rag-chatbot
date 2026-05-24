export function buildSuggestions(answer) {
  const text = answer.toLowerCase();

  if (
    text.includes("no tengo suficiente información") ||
    text.includes("no se pudo generar")
  ) {
    return [
      "¿Sobre qué temas puedes responder?",
      "¿Qué es Latinoamérica Comparte?",
      "¿Qué programas tiene Comparte Academia?",
    ];
  }

  if (text.includes("estructura")) {
    return [
      "¿Qué temas trabaja ESTRUCTURA?",
      "¿Cuánto dura ESTRUCTURA?",
      "¿Para quién está diseñado ESTRUCTURA?",
    ];
  }

  if (text.includes("deskubre")) {
    return [
      "¿Qué es DESKUBRE?",
      "¿Cuánto dura DESKUBRE?",
      "¿Para quién sirve DESKUBRE?",
    ];
  }

  if (text.includes("comparte liderazgo")) {
    return [
      "¿Qué es Comparte Liderazgo?",
      "¿A qué empresas puede servir Comparte Liderazgo?",
      "¿Qué busca desarrollar Comparte Liderazgo?",
    ];
  }

  if (text.includes("comparte talento")) {
    return [
      "¿Qué es Comparte Talento?",
      "¿Comparte Talento sirve para eventos?",
      "¿Comparte Talento ofrece speakers?",
    ];
  }

  if (text.includes("comparte academia")) {
    return [
      "¿Qué programas tiene Comparte Academia?",
      "¿Qué es DESKUBRE?",
      "¿Qué es ESTRUCTURA?",
    ];
  }

  return [
    "¿Qué es Latinoamérica Comparte?",
    "¿Qué es Comparte Academia?",
    "¿A cuántas personas han acompañado?",
  ];
}