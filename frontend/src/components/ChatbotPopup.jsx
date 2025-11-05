import React, { useState } from 'react';

const GEMINI_API_KEY = 'AIzaSyB8z_fUYkylyz9_DT1N3e3ZEGJXqRfkqic';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

function ChatbotPopup() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setLoading(true);
    setInput('');
    try {
      const res = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: input }] }]
        })
      });
      const data = await res.json();
      const botText = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'No response.';
      setMessages([...messages, userMessage, { role: 'bot', content: botText }]);
    } catch (e) {
      setMessages([...messages, userMessage, { role: 'bot', content: 'Error contacting Gemini API.' }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 1000 }}>
      {open ? (
        <div style={{ width: 320, background: '#fff', borderRadius: 8, boxShadow: '0 2px 12px rgba(0,0,0,0.15)', padding: 16 }}>
          <div style={{ maxHeight: 300, overflowY: 'auto', marginBottom: 8 }}>
            {messages.map((msg, i) => (
              <div key={i} style={{ textAlign: msg.role === 'user' ? 'right' : 'left', margin: '4px 0' }}>
                <span style={{ background: msg.role === 'user' ? '#e0f7fa' : '#f1f8e9', padding: '6px 12px', borderRadius: 6 }}>{msg.content}</span>
              </div>
            ))}
            {loading && <div style={{ textAlign: 'center', color: '#888' }}>Thinking...</div>}
          </div>
          <div style={{ display: 'flex' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' ? sendMessage() : null}
              style={{ flex: 1, padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()} style={{ marginLeft: 8, padding: '8px 16px', borderRadius: 4, background: '#1976d2', color: '#fff', border: 'none' }}>Send</button>
          </div>
          <button onClick={() => setOpen(false)} style={{ marginTop: 8, background: 'none', border: 'none', color: '#1976d2', cursor: 'pointer' }}>Close</button>
        </div>
      ) : (
        <button onClick={() => setOpen(true)} style={{ background: '#1976d2', color: '#fff', borderRadius: '50%', width: 56, height: 56, border: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.2)', fontSize: 24, cursor: 'pointer' }}>💬</button>
      )}
    </div>
  );
}

export default ChatbotPopup;
