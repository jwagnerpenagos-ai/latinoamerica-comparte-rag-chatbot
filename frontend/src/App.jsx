import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import ChatLauncher from "./components/chat/ChatLauncher";
import ChatOverlay from "./components/chat/ChatOverlay";
import { useChat } from "./hooks/useChat";

function App() {
  const {
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
  } = useChat();

  return (
    <main className="app">
      <Navbar />
      <Hero />

      {!isChatOpen && <ChatLauncher onOpen={openChat} />}

      {isChatOpen && (
        <ChatOverlay
          mode={chatMode}
          messages={messages}
          suggestions={suggestions}
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          onClose={closeChat}
          onSubmit={handleSubmit}
          onSuggestionClick={sendQuestion}
          onClear={clearChat}
          onToggleMode={toggleChatMode}
        />
      )}
    </main>
  );
}

export default App;