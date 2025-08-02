
import { useState } from 'react';

const API_BASE = 'http://localhost:8000'; // Change if needed

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [selectedDocs, setSelectedDocs] = useState('');
  const [loading, setLoading] = useState(false);

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
    alert(res.ok ? 'File ingested!' : 'Error ingesting file');
  };

  const handleQuery = async () => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setAnswer(data.answer || 'No answer');
    setLoading(false);
  };

  const handleSelectDocs = async () => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/select-docs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ docs: selectedDocs.split(',') }),
    });
    setLoading(false);
    alert(res.ok ? 'Documents selected!' : 'Error selecting documents');
  };

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h2>Document-RAG Demo</h2>
      <section style={{ marginBottom: '2rem' }}>
        <h3>1. Ingest Document</h3>
        <input type="file" accept=".pdf,.txt,.docx" onChange={handleFileChange} />
        <button onClick={handleIngest} disabled={loading || !file} style={{ marginLeft: 8 }}>Ingest</button>
      </section>
      <section style={{ marginBottom: '2rem' }}>
        <h3>2. Query</h3>
        <input type="text" value={question} onChange={e => setQuestion(e.target.value)} placeholder="Ask a question..." style={{ width: '80%' }} />
        <button onClick={handleQuery} disabled={loading || !question} style={{ marginLeft: 8 }}>Query</button>
        <div style={{ marginTop: 12 }}><strong>Answer:</strong> {answer}</div>
      </section>
      <section>
        <h3>3. Select Documents for RAG</h3>
        <input type="text" value={selectedDocs} onChange={e => setSelectedDocs(e.target.value)} placeholder="doc1,doc2,..." style={{ width: '80%' }} />
        <button onClick={handleSelectDocs} disabled={loading || !selectedDocs} style={{ marginLeft: 8 }}>Select Docs</button>
      </section>
      {loading && <div style={{ marginTop: 20 }}>Loading...</div>}
    </div>
  );
}

export default App;
