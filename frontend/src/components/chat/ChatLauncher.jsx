function ChatLauncher({ onOpen }) {
  return (
    <button
      className="chat-launcher"
      onClick={onOpen}
      aria-label="Abrir asistente"
      title="Abrir asistente"
    >
      <img src="/Chatbot.svg" alt="Asistente Latinoamérica Comparte" />
    </button>
  );
}

export default ChatLauncher;