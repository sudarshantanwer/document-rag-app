// API utility functions for the frontend
export const API_BASE = 'http://localhost:8000';

export const apiService = {
  // Fetch all documents
  async fetchDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.status}`);
    }
    return response.json();
  },

  // Ingest a document
  async ingestDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/ingest`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to ingest document: ${response.status}`);
    }
    return response.json();
  },

  // Query documents
  async queryDocuments(question, selectedDoc = null) {
    const payload = { question };
    if (selectedDoc) {
      payload.doc_id = selectedDoc;
    }

    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Failed to query documents: ${response.status}`);
    }
    return response.json();
  },

  // Select documents for RAG
  async selectDocuments(docIds) {
    const response = await fetch(`${API_BASE}/select-docs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ doc_ids: docIds }),
    });

    if (!response.ok) {
      throw new Error(`Failed to select documents: ${response.status}`);
    }
    return response.json();
  }
};
