import { User } from "lucide-react";

function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      {!isUser && (
        <div className="message-icon bot-image-icon">
          <img src="/Chatbot.svg" alt="Asistente" />
        </div>
      )}

      <div className="message-bubble">{message.content}</div>

      {isUser && (
        <div className="message-icon user-icon">
          <User size={18} />
        </div>
      )}
    </div>
  );
}

export default ChatMessage;