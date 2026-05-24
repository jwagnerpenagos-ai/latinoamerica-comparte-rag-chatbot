function ChatLauncher({ onOpen }) {
  return (
    <button
      className="chat-launcher"
      onClick={onOpen}
      aria-label="Abrir asistente"
    >
      <img src="/Chatbot.svg" alt="" />
    </button>
  );
}

export default ChatLauncher;