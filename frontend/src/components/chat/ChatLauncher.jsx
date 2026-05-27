function ChatLauncher({ onOpen }) {
  return (
    <button
      className="chat-launcher"
      onClick={onOpen}
      aria-label="Abrir asistente"
      title="Abrir asistente"
    >
     <img
      className="chat-launcher-image"
      src="/colibri-chatbot.png"
      alt="Asistente Latinoamérica Comparte"
/>
    </button>
  );
}

export default ChatLauncher;