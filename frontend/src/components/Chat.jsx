import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2, PlayCircle, MessageCircle } from 'lucide-react';
import { BASE_URL } from '../api/client';

const Chat = ({ activeUserId }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hello! I'm your movie assistant. What kind of films are you in the mood for today?", recommendations: [], reasoning: '' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recommenderType, setRecommenderType] = useState('rag'); // few_shot, rag, agent
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessage = { role: 'assistant', text: '', recommendations: [], reasoning: '', status: 'generating' };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch(`${BASE_URL}/api/v1/recommend/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_history: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.text || m.content
          })),
          user_id: activeUserId,
          recommender_type: recommenderType,
          num_recommendations: 5,
          temperature: 0.7
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') break;

            try {
              const data = JSON.parse(dataStr);
              setMessages(prev => {
                const last = { ...prev[prev.length - 1] };
                if (data.type === 'recommendation') {
                  last.recommendations = [...(last.recommendations || []), data.movie];
                } else if (data.type === 'reasoning') {
                  last.text += data.content;
                } else if (data.type === 'error') {
                  last.text = `Error: ${data.content}`;
                }
                return [...prev.slice(0, -1), last];
              });
            } catch (e) {
              console.error('Error parsing SSE data:', e, dataStr);
            }
          }
        }
      }
    } catch (err) {
      console.error('Streaming failed:', err);
      setMessages(prev => {
        const last = { ...prev[prev.length - 1], text: 'Sorry, I encountered an error connecting to the API.', status: 'error' };
        return [...prev.slice(0, -1), last];
      });
    } finally {
      setIsLoading(false);
      setMessages(prev => {
        const last = { ...prev[prev.length - 1], status: 'done' };
        return [...prev.slice(0, -1), last];
      });
    }
  };

  return (
    <main style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '0 1rem 1rem 1rem', overflow: 'hidden' }}>
      <div className="glass" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Chat Header - Recommender Mode Selector */}
        <div style={{ 
          padding: '1rem 1.5rem', 
          borderBottom: '2px solid rgba(99, 102, 241, 0.2)', 
          background: 'rgba(255, 255, 255, 0.02)',
          display: 'flex', 
          flexDirection: 'column',
          gap: '0.75rem',
          zIndex: 10
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <MessageCircle size={16} color="var(--brand-primary-light)" />
              <h2 style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
                Response Mode
              </h2>
            </div>
            <div style={{ padding: '0.25rem 0.6rem', background: 'var(--brand-primary-dim)', borderRadius: '4px', fontSize: '0.65rem', fontWeight: '700', color: 'var(--brand-primary-light)' }}>
              {recommenderType.toUpperCase().replace('_', ' ')} ACTIVE
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {['few_shot', 'rag', 'agent'].map(type => (
              <button
                key={type}
                onClick={() => setRecommenderType(type)}
                style={{
                  flex: 1,
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  padding: '0.6rem',
                  borderRadius: '10px',
                  background: recommenderType === type ? 'var(--brand-primary)' : 'rgba(255,255,255,0.04)',
                  color: 'white',
                  border: '1px solid',
                  borderColor: recommenderType === type ? 'var(--brand-primary-light)' : 'var(--border-color)',
                  transition: 'all 0.2s ease',
                  boxShadow: recommenderType === type ? '0 4px 12px rgba(99, 102, 241, 0.3)' : 'none',
                  textTransform: 'capitalize'
                }}
              >
                {type.replace('_', ' ')}
              </button>
            ))}
          </div>
          
          <button 
            onClick={() => setMessages([{ role: 'assistant', text: "Hello! I'm your movie assistant. What kind of films are you in the mood for today?", recommendations: [], reasoning: '' }])}
            style={{ 
              fontSize: '0.7rem', 
              color: 'var(--text-tertiary)', 
              textAlign: 'center', 
              marginTop: '0.25rem',
              padding: '0.25rem',
              textDecoration: 'underline'
            }}
            onMouseEnter={(e) => e.target.style.color = 'var(--text-secondary)'}
            onMouseLeave={(e) => e.target.style.color = 'var(--text-tertiary)'}
          >
            Clear Conversation
          </button>
        </div>

        {/* Chat Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
              gap: '0.5rem',
              animation: 'fadeIn 0.3s ease-out'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                {msg.role === 'assistant' ? <Bot size={14} color="var(--brand-primary)" /> : <User size={14} color="var(--text-secondary)" />}
                <span style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-tertiary)' }}>
                  {msg.role === 'assistant' ? 'AI RECOMMENDER' : 'YOU'}
                </span>
              </div>
              
              <div style={{ 
                maxWidth: '80%', 
                padding: '1rem', 
                borderRadius: '16px', 
                background: msg.role === 'user' ? 'var(--brand-primary)' : 'rgba(255,255,255,0.03)',
                border: msg.role === 'user' ? 'none' : '1px solid var(--border-color)',
                color: msg.role === 'user' ? 'white' : 'var(--text-primary)',
                fontSize: '0.925rem'
              }}>
                {msg.text}
                
                {msg.recommendations && msg.recommendations.length > 0 && (
                  <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem' }}>
                    {msg.recommendations.map((movie, idx) => (
                      <div key={idx} className="glass" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', position: 'relative', overflow: 'hidden' }}>
                        <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'var(--brand-primary)' }}></div>
                        <h4 style={{ fontSize: '0.875rem', fontWeight: '700', marginBottom: '0.5rem' }}>{movie}</h4>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--brand-primary-light)', fontSize: '0.75rem', fontWeight: '600' }}>
                          <PlayCircle size={14} />
                          <span>View Details</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {msg.status === 'generating' && msg.text === '' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-tertiary)' }}>
                    <Loader2 size={16} className="animate-spin" />
                    <span style={{ fontSize: '0.8rem' }}>Thinking...</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ 
            display: 'flex', 
            background: 'var(--bg-primary)', 
            border: '1px solid var(--border-color)', 
            borderRadius: '14px', 
            padding: '0.5rem',
            transition: 'var(--transition-fast)',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
          onFocusCapture={(e) => e.currentTarget.style.borderColor = 'var(--brand-primary)'}
          onBlurCapture={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
          >
            <input
              type="text"
              placeholder="Tell me about your favorite movies or what you want to see..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              style={{ flex: 1, background: 'none', border: 'none', padding: '0.75rem 1rem', color: 'white', fontSize: '0.9375rem' }}
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              style={{ 
                background: input.trim() ? 'var(--brand-primary)' : 'rgba(255,255,255,0.05)', 
                color: 'white', 
                borderRadius: '10px', 
                padding: '0 1.25rem',
                opacity: (isLoading || !input.trim()) ? 0.5 : 1
              }}
            >
              <Send size={18} />
            </button>
          </div>
          <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '1rem', color: 'var(--text-tertiary)', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Sparkles size={12} color="var(--brand-primary)" />
              <span>AI-Powered Insights</span>
            </div>
            <span>•</span>
            <span>Dataset: LLM-REDIAL</span>
          </div>
        </div>
      </div>
    </main>
  );
};

export default Chat;
