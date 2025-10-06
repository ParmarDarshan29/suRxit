import React, { useState, useRef } from 'react';
import { useChatAPI } from '../services/apiServices';

/**
 * ChatbotWidget
 * Floating MedLM-powered assistant for Q&A, context-aware.
 * Props: none (API URL from env)
 */
export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);
  const { sendMessage: sendChatMessage } = useChatAPI();

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    const currentInput = input;
    setInput('');
    setLoading(true);
    
    try {
      const response = await sendChatMessage(currentInput, messages);
      
      if (response?.message) {
        setMessages((msgs) => [...msgs, { role: 'assistant', content: response.message }]);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Chat API Error:', err);
      const errorMsg = err.message.includes('401') 
        ? 'Please log in to continue chatting.'
        : 'Sorry, I could not answer that. Please try again later.';
      setMessages((msgs) => [...msgs, { role: 'assistant', content: errorMsg }]);
    } finally {
      setLoading(false);
      setTimeout(() => {
        if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
      }, 100);
    }
  }

  return (
    <>
      <button
        className="fixed bottom-6 right-6 z-50 bg-blue-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-blue-700 focus:outline-none"
        aria-label="Open Chatbot"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="text-2xl">💬</span>
      </button>
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-80 max-w-full bg-white rounded-lg shadow-2xl border flex flex-col">
          <div className="flex items-center justify-between px-4 py-2 border-b bg-blue-600 text-white rounded-t-lg">
            <span className="font-bold">MedLM Assistant</span>
            <button onClick={() => setOpen(false)} aria-label="Close" className="text-xl">×</button>
          </div>
          <div ref={chatRef} className="flex-1 overflow-y-auto p-4 space-y-2" style={{ maxHeight: 320 }}>
            {messages.length === 0 && <div className="text-gray-400 text-sm">Ask about prescriptions, risks, foods to avoid, safer alternatives…</div>}
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                <span className={msg.role === 'user' ? 'inline-block bg-blue-100 text-blue-900 rounded px-2 py-1' : 'inline-block bg-gray-100 text-gray-800 rounded px-2 py-1'}>
                  {msg.content}
                </span>
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="flex border-t">
            <input
              className="flex-1 px-3 py-2 rounded-bl-lg focus:outline-none"
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type your question…"
              disabled={loading}
              aria-label="Chat input"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-br-lg hover:bg-blue-700 disabled:opacity-50"
              disabled={loading || !input.trim()}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
