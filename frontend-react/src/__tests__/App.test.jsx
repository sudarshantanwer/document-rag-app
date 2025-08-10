import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

// Mock fetch API
global.fetch = jest.fn();

// Mock file for testing
const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders main components', () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    render(<App />);
    
    expect(screen.getByText(/Document-RAG Demo/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ingest/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /query/i })).toBeInTheDocument();
  });

  test('fetches documents on load', async () => {
    const mockDocuments = [
      { id: '1', filename: 'doc1.txt', created_at: '2024-01-01' },
      { id: '2', filename: 'doc2.txt', created_at: '2024-01-02' }
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: mockDocuments })
    });

    render(<App />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/documents');
    });
  });

  test('handles file selection', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    const user = userEvent.setup();
    const { container } = render(<App />);

    const fileInput = container.querySelector('input[type="file"]');
    await user.upload(fileInput, mockFile);

    expect(fileInput.files[0]).toBe(mockFile);
    expect(fileInput.files).toHaveLength(1);
  });

  test('handles document ingestion', async () => {
    // Mock initial document fetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    // Mock successful ingestion
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'Document processed successfully' })
    });

    // Mock document fetch after ingestion
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [{ id: '1', filename: 'test.txt' }] })
    });

    const user = userEvent.setup();
    const { container } = render(<App />);

    // Upload file
    const fileInput = container.querySelector('input[type="file"]');
    await user.upload(fileInput, mockFile);

    // Click ingest button
    const ingestButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(ingestButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/ingest', {
        method: 'POST',
        body: expect.any(FormData)
      });
    });

    // Should refetch documents after successful ingestion
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(3); // Initial fetch + ingest + refetch
    });
  });

  test('handles query submission', async () => {
    // Mock initial document fetch with some documents
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        documents: [
          { id: '1', filename: 'doc1.txt', created_at: '2024-01-01' },
          { id: '2', filename: 'doc2.txt', created_at: '2024-01-02' }
        ]
      })
    });

    // Mock successful query
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ 
        answer: 'This is the answer',
        sources: ['doc1.txt', 'doc2.txt']
      })
    });

    const user = userEvent.setup();
    render(<App />);

    // Wait for documents to load and select one
    await waitFor(() => {
      expect(screen.getByText('doc1.txt')).toBeInTheDocument();
    });

    const documentSelect = screen.getByRole('combobox');
    await user.selectOptions(documentSelect, '1');

    // Enter question
    const questionInput = screen.getByPlaceholderText(/ask a question/i);
    await user.type(questionInput, 'What is this about?');

    // Submit query
    const queryButton = screen.getByRole('button', { name: /query/i });
    await user.click(queryButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: 'What is this about?', doc_id: '1' })
      });
    });
  });

  test('displays loading state during ingestion', async () => {
    // Mock initial document fetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    // Mock slow ingestion response
    let resolveIngest;
    const ingestPromise = new Promise(resolve => {
      resolveIngest = resolve;
    });
    fetch.mockReturnValueOnce(ingestPromise);

    const user = userEvent.setup();
    const { container } = render(<App />);

    // Upload file and start ingestion
    const fileInput = container.querySelector('input[type="file"]');
    await user.upload(fileInput, mockFile);

    const ingestButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(ingestButton);

    // Should show loading state (the loading indicator contains "Loading..." text)
    await waitFor(() => {
      expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });

    // Resolve the ingestion
    resolveIngest({
      ok: true,
      json: async () => ({ status: 'success' })
    });

    // Mock refetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    await waitFor(() => {
      expect(screen.queryByText(/ingesting/i)).not.toBeInTheDocument();
    });
  });

  test('handles query with empty question', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    const user = userEvent.setup();
    render(<App />);

    // Try to submit empty query
    const queryButton = screen.getByRole('button', { name: /query/i });
    await user.click(queryButton);

    // Should not make API call with empty question
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1); // Only initial documents fetch
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock initial document fetch failure  
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => ({ error: 'Server error' })
    });

    render(<App />);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/documents');
    });

    // Component should still render despite fetch error
    expect(screen.getByText(/Document-RAG Demo/i)).toBeInTheDocument();
  });

  test('handles ingestion error', async () => {
    // Mock initial document fetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ documents: [] })
    });

    // Mock ingestion error
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    const user = userEvent.setup();
    const { container } = render(<App />);

    const fileInput = container.querySelector('input[type="file"]');
    await user.upload(fileInput, mockFile);

    const ingestButton = screen.getByRole('button', { name: /ingest/i });
    await user.click(ingestButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/ingest', {
        method: 'POST',
        body: expect.any(FormData)
      });
    });

    // Should handle error gracefully - component stays functional
    expect(screen.getByRole('button', { name: /ingest/i })).toBeInTheDocument();
  });
});
