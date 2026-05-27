import ChatWindow from "./ChatWindow";

function ChatOverlay({
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
  const isExpanded = mode === "expanded";

  const handleOverlayMouseDown = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={`chat-overlay ${isExpanded ? "expanded" : "dock"}`}
      onMouseDown={handleOverlayMouseDown}
    >
      <ChatWindow
        mode={mode}
        messages={messages}
        suggestions={suggestions}
        input={input}
        setInput={setInput}
        isLoading={isLoading}
        onClose={onClose}
        onSubmit={onSubmit}
        onSuggestionClick={onSuggestionClick}
        onClear={onClear}
        onToggleMode={onToggleMode}
      />
    </div>
  );
}

export default ChatOverlay;