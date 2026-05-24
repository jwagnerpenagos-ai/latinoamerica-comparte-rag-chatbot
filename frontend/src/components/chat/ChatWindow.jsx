import { useEffect, useRef } from "react";
import {
  Send,
  X,
  Bot,
  Loader2,
  Maximize2,
  Minimize2,
} from "lucide-react";
import ChatMessage from "./ChatMessage";

function ChatWindow({
  mode,
  messages,
  suggestions,
  input,
  setInput,
  isLoading,
  onClose,
  onSubmit,
  onSuggestionClick,
  onClear,
  onToggleMode,
}) {
  const messagesEndRef = useRef(null);
  const isExpanded = mode === "expanded";

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isLoading]);

  return (
    <section
      className={`chat-window ${isExpanded ? "expanded" : "dock"}`}
      id="chat"
      onMouseDown={(event) => event.stopPropagation()}
    >
      <header className="chat-header">
        <div className="chat-title-box">
          <div className="chat-avatar">
            <Bot size={20} />
          </div>

          <div className="chat-title-text">
            <h3>Asistente Latinoamérica Comparte</h3>
            <p>Programas, impacto, historia y colaboración.</p>
          </div>
        </div>

        <div className="chat-header-actions">
          <button
            className="icon-button"
            type="button"
            onClick={onToggleMode}
            aria-label={isExpanded ? "Reducir chat" : "Agrandar chat"}
            title={isExpanded ? "Reducir chat" : "Agrandar chat"}
          >
            {isExpanded ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>

          <button
            className="icon-button"
            type="button"
            onClick={onClose}
            aria-label="Cerrar chat"
            title="Cerrar chat"
          >
            <X size={19} />
          </button>
        </div>
      </header>

      <div className="messages">
        {messages.length === 0 && !isLoading && (
          <div className="empty-chat">
            <div className="empty-icon">💬</div>
            <h4>Haz tu primera pregunta</h4>
            <p>
              Pregunta por DESKUBRE, ESTRUCTURA, Comparte Academia, Liderazgo,
              Talento, impacto o formas de colaboración.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={`${message.role}-${index}`} message={message} />
        ))}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-icon">
              <Bot size={16} />
            </div>

            <div className="message-bubble loading">
              <Loader2 size={16} className="spin" />
              Consultando la base de conocimiento...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <footer className="composer-area">
        {suggestions.length > 0 && (
          <div className="suggestion-float">
            {suggestions.slice(0, 3).map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => onSuggestionClick(suggestion)}
                disabled={isLoading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <form className="chat-form" onSubmit={onSubmit}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Escribe tu pregunta..."
            disabled={isLoading}
          />

          <button type="submit" disabled={isLoading || !input.trim()}>
            <Send size={17} />
          </button>
        </form>

        <div className="chat-actions">
          <button type="button" onClick={onClear} disabled={isLoading}>
            Limpiar conversación
          </button>
        </div>
      </footer>
    </section>
  );
}

export default ChatWindow;