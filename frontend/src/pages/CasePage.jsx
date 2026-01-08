import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function CasePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'docs' | 'strategy'
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Chat State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  // Docs State
  const [uploading, setUploading] = useState(false);

  // Strategy State
  const [strategy, setStrategy] = useState(null);
  const [generatingStrategy, setGeneratingStrategy] = useState(false);

  useEffect(() => {
    fetchCaseDetails();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, activeTab]);

  const fetchCaseDetails = async () => {
    try {
      const res = await api.get(`/cases/${id}`);
      setCaseData(res.data);
      const sortedMsgs = (res.data.messages || []).sort((a,b) => 
        new Date(a.created_at) - new Date(b.created_at)
      );
      setMessages(sortedMsgs);
    } catch (err) {
      alert("Error loading case");
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // --- ACTIONS ---

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Optimistic UI Update
    const tempMsg = { sender: 'user', content: input, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, tempMsg]);
    setInput('');
    setSending(true);

    try {
      const res = await api.post(`/cases/${id}/messages`, { content: tempMsg.content });
      setMessages(prev => [...prev.slice(0, -1), res.data.user_message_obj, {
        sender: 'ai',
        content: res.data.ai_response,
        created_at: new Date().toISOString()
      }]);

      const aiMsg = { sender: 'ai', content: res.data.ai_response, created_at: new Date().toISOString() };
      setMessages(prev => [...prev, aiMsg]);

    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      await api.post(`/cases/${id}/documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert("File uploaded! Processing started.");
      fetchCaseDetails(); 
    } catch (err) {
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateStrategy = async () => {
    setGeneratingStrategy(true);
    try {
      const res = await api.post(`/cases/${id}/strategy`);
      let strat = res.data.strategy;
      if (typeof strat === 'string') {
        try { strat = JSON.parse(strat); } catch(e) { console.log("Not JSON string"); }
      }
      setStrategy(strat);
    } catch (err) {
      alert("Failed to generate strategy. Make sure you have uploaded documents first.");
    } finally {
      setGeneratingStrategy(false);
    }
  };

  if (loading) return <div className="p-10 text-center">Loading Case...</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm z-10">
        <div>
          <button onClick={() => navigate('/dashboard')} className="text-sm text-gray-500 hover:text-lex-600 mb-1">
            ← Back to Dashboard
          </button>
          <h1 className="text-xl font-bold text-gray-900">{caseData?.title}</h1>
          <span className="text-xs text-gray-500 uppercase tracking-wider">{caseData?.category} • {caseData?.status}</span>
        </div>
        
        {/* Tab Switcher */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          {['chat', 'docs', 'strategy'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab 
                  ? 'bg-white text-lex-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative">
        
        {/* --- CHAT TAB --- */}
        {activeTab === 'chat' && (
          <div className="h-full flex flex-col max-w-4xl mx-auto bg-white shadow-xl border-x">
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.length === 0 && (
                <div className="text-center text-gray-400 mt-10">
                  <p>No messages yet. Ask LexGuard anything about this case.</p>
                </div>
              )}
              
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    msg.sender === 'user' 
                      ? 'bg-lex-600 text-white rounded-br-none' 
                      : 'bg-gray-100 text-gray-800 rounded-bl-none'
                  }`}>
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                  </div>
                </div>
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-500 rounded-2xl px-5 py-3 rounded-bl-none animate-pulse">
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t bg-gray-50">
              <form onSubmit={handleSendMessage} className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a legal question about your documents..."
                  className="flex-1 p-3 border rounded-xl focus:ring-2 focus:ring-lex-500 outline-none shadow-sm"
                />
                <button 
                  type="submit" 
                  disabled={sending}
                  className="bg-lex-600 hover:bg-lex-700 text-white px-6 rounded-xl font-medium transition-colors disabled:opacity-50"
                >
                  Send
                </button>
              </form>
            </div>
          </div>
        )}

        {/* --- DOCUMENTS TAB --- */}
        {activeTab === 'docs' && (
          <div className="p-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Case Documents</h2>
              <label className="bg-lex-600 hover:bg-lex-700 text-white px-4 py-2 rounded-lg cursor-pointer shadow-sm transition-colors">
                {uploading ? "Uploading..." : "+ Upload PDF"}
                <input type="file" accept=".pdf,.txt" className="hidden" onChange={handleFileUpload} disabled={uploading} />
              </label>
            </div>

            <div className="grid gap-4">
              {caseData?.documents?.length === 0 && <p className="text-gray-500">No documents uploaded yet.</p>}
              
              {caseData?.documents?.map(doc => (
                <div key={doc.id} className="bg-white p-4 rounded-lg border flex justify-between items-center shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="bg-red-100 text-red-600 p-2 rounded">PDF</div>
                    <div>
                      <p className="font-medium text-gray-900">{doc.filename}</p>
                      <p className="text-xs text-gray-500">Uploaded on {new Date(doc.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                    {doc.analysis_json ? "Analyzed" : "Processing"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* --- STRATEGY TAB --- */}
        {activeTab === 'strategy' && (
          <div className="p-8 max-w-4xl mx-auto overflow-y-auto h-full">
            {!strategy ? (
              <div className="text-center py-20">
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Strategy Generated Yet</h3>
                <p className="text-gray-500 mb-6">Upload documents first, then ask AI to formulate a legal strategy.</p>
                <button 
                  onClick={handleGenerateStrategy}
                  disabled={generatingStrategy}
                  className="bg-lex-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-lex-700 disabled:opacity-50"
                >
                  {generatingStrategy ? "Generating..." : "Generate Legal Strategy"}
                </button>
              </div>
            ) : (
              <div className="space-y-6 pb-20">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                  <h3 className="font-bold text-blue-800">Executive Summary</h3>
                  <p className="text-blue-900">{strategy.summary || "No summary available."}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-xl border shadow-sm">
                    <h3 className="font-bold text-green-700 mb-4 flex items-center gap-2">🛡️ Safe Approach</h3>
                    <ul className="space-y-2">
                      {strategy.safe_plan?.map((step, i) => (
                        <li key={i} className="flex gap-2 text-sm text-gray-700">
                          <span className="font-bold text-green-600">{i+1}.</span> {step}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-white p-6 rounded-xl border shadow-sm">
                    <h3 className="font-bold text-orange-700 mb-4 flex items-center gap-2">⚔️ Aggressive Approach</h3>
                    <ul className="space-y-2">
                      {strategy.aggressive_plan?.map((step, i) => (
                        <li key={i} className="flex gap-2 text-sm text-gray-700">
                          <span className="font-bold text-orange-600">{i+1}.</span> {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}