


import React, { useState, useEffect } from 'react';
import './custom.css';

const API_BASE = 'http://localhost:8000'; // Change if needed



function App() {
  const loadingRef = React.useRef(null);
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [selectedDoc, setSelectedDoc] = useState("");
  const [allDocs, setAllDocs] = useState([]);
  // ...existing code...
  const [loading, setLoading] = useState(false);
  // Fetch all available documents on load and expose fetchDocs for reuse
  const fetchDocs = async () => {
    const res = await fetch(`${API_BASE}/documents`);
    if (res.ok) {
      const data = await res.json();
      setAllDocs(data.documents || []);
    }
  };
  useEffect(() => {
    fetchDocs();
  }, []);



  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleIngest = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/ingest`, {
      method: 'POST',
      body: formData,
    });
    setLoading(false);
    if (res.ok) {
      await fetchDocs(); // Refresh document list after successful ingest
    }
    alert(res.ok ? 'File ingested!' : 'Error ingesting file');
  };

  const handleQuery = async () => {
    if (!selectedDoc) {
      alert('Please select a document before querying.');
      return;
    }
    setLoading(true);
    setTimeout(() => {
      if (loadingRef.current) {
        loadingRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100); // allow loading to render
    const res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, doc_id: selectedDoc }),
    });
    const data = await res.json();
    setAnswer(data.answer || 'No answer');
    setLoading(false);
  };

  const handleSelectDocs = async () => {
    if (!selectedDoc) return;
    setLoading(true);
    const res = await fetch(`${API_BASE}/select-docs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_ids: [selectedDoc] }),
    });
    setLoading(false);
    alert(res.ok ? 'Document selected!' : 'Error selecting document');
  };

  return (
    <div className="custom-bg">
      <div className="custom-card">
        <img src="/src/assets/ai-logo.svg" alt="AI Logo" style={{width: 80, height: 80, marginBottom: 16}} />
        <h2 className="custom-title">Document-RAG Demo</h2>

        {/* Ingest Document */}
        <section className="custom-section">
          <h3 className="custom-section-title">1. Ingest Document</h3>
          <div className="custom-row">
            <input type="file" accept=".pdf,.txt,.docx" onChange={handleFileChange} className="custom-input" />
            <button onClick={handleIngest} disabled={loading || !file} className="custom-btn">Ingest</button>
          </div>
        </section>

        {/* Select Document */}
        <section className="custom-section">
          <h3 className="custom-section-title">2. Select Document for RAG</h3>
          <div className="custom-row">
            <select
              value={selectedDoc}
              onChange={e => setSelectedDoc(e.target.value)}
              className="custom-input"
            >
              <option value="">Select a document...</option>
              {allDocs.map(doc => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
            <button onClick={handleSelectDocs} disabled={loading || !selectedDoc} className="custom-btn">Select Doc</button>
          </div>
        </section>

        {/* Query Section */}
        <section className="custom-section">
          <h3 className="custom-section-title">3. Query</h3>
          <div className="custom-row">
            <input
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Ask a question..."
              className="custom-input"
            />
            <button onClick={handleQuery} disabled={loading || !question} className="custom-btn">Query</button>
          </div>
          <div className="custom-answer-box">
            <span className="custom-answer-label">Answer:</span> <span className="custom-answer">{answer}</span>
          </div>
        </section>

        {loading && (
          <div className="custom-loading" ref={loadingRef}>
            <div className="loader-spinner" />
            <div style={{marginTop: 12}}>Loading...</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
