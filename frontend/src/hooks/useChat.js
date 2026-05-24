import { useState } from "react";
import { API_URL } from "../constants/site";
import { buildSuggestions } from "../utils/suggestions";

export function useChat() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMode, setChatMode] = useState("dock");
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  const openChat = () => {
    setChatMode("dock");
    setIsChatOpen(true);
  };

  const closeChat = () => {
    setIsChatOpen(false);
    setChatMode("dock");
  };

  const toggleChatMode = () => {
    setChatMode((currentMode) =>
      currentMode === "dock" ? "expanded" : "dock"
    );
  };

  const sendQuestion = async (question) => {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || isLoading) return;

    const userMessage = {
      role: "user",
      content: cleanQuestion,
    };

    setMessages((previousMessages) => [...previousMessages, userMessage]);
    setSuggestions([]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: cleanQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("No se pudo conectar con la API.");
      }

      const data = await response.json();

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);

      setSuggestions(buildSuggestions(data.answer));
    } catch (error) {
      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content:
            "Ocurrió un error al consultar el asistente. Verifica que el backend esté corriendo en http://localhost:8000.",
        },
      ]);

      setSuggestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    sendQuestion(input);
  };

  const clearChat = () => {
    setMessages([]);
    setSuggestions([]);
  };

  return {
    isChatOpen,
    chatMode,
    input,
    setInput,
    isLoading,
    messages,
    suggestions,
    openChat,
    closeChat,
    toggleChatMode,
    sendQuestion,
    handleSubmit,
    clearChat,
  };
}