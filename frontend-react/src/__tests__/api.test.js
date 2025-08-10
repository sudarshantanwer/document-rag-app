import { apiService } from '../api';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('fetchDocuments', () => {
    test('fetches documents successfully', async () => {
      const mockDocuments = {
        documents: [
          { id: '1', filename: 'doc1.txt', created_at: '2024-01-01' },
          { id: '2', filename: 'doc2.txt', created_at: '2024-01-02' }
        ]
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDocuments
      });

      const result = await apiService.fetchDocuments();

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/documents');
      expect(result).toEqual(mockDocuments);
    });

    test('throws error when fetch fails', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      });

      await expect(apiService.fetchDocuments()).rejects.toThrow('Failed to fetch documents: 500');
    });
  });

  describe('ingestDocument', () => {
    test('ingests document successfully', async () => {
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const mockResponse = {
        status: 'Document processed successfully',
        doc_id: '123e4567-e89b-12d3-a456-426614174000'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.ingestDocument(mockFile);

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/ingest', {
        method: 'POST',
        body: expect.any(FormData)
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws error when ingestion fails', async () => {
      const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400
      });

      await expect(apiService.ingestDocument(mockFile)).rejects.toThrow('Failed to ingest document: 400');
    });
  });

  describe('queryDocuments', () => {
    test('queries documents successfully', async () => {
      const mockResponse = {
        answer: 'This is the answer',
        sources: ['doc1.txt', 'doc2.txt']
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.queryDocuments('What is this about?');

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: 'What is this about?' }),
      });
      expect(result).toEqual(mockResponse);
    });

    test('queries with specific document', async () => {
      const mockResponse = {
        answer: 'Specific answer',
        sources: ['specific-doc.txt']
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.queryDocuments('Question?', 'doc-123');

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question: 'Question?',
          doc_id: 'doc-123'
        }),
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws error when query fails', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      });

      await expect(apiService.queryDocuments('Question?')).rejects.toThrow('Failed to query documents: 500');
    });
  });

  describe('selectDocuments', () => {
    test('selects documents successfully', async () => {
      const mockResponse = {
        selected_docs: ['doc1', 'doc2'],
        status: 'Documents selected successfully'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.selectDocuments(['doc1', 'doc2']);

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/select-docs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ doc_ids: ['doc1', 'doc2'] }),
      });
      expect(result).toEqual(mockResponse);
    });

    test('throws error when selection fails', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400
      });

      await expect(apiService.selectDocuments(['doc1'])).rejects.toThrow('Failed to select documents: 400');
    });

    test('handles empty document list', async () => {
      const mockResponse = {
        error: 'No doc_ids provided'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.selectDocuments([]);

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/select-docs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ doc_ids: [] }),
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Network errors', () => {
    test('handles network errors in fetchDocuments', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.fetchDocuments()).rejects.toThrow('Network error');
    });

    test('handles network errors in ingestDocument', async () => {
      const mockFile = new File(['test'], 'test.txt', { type: 'text/plain' });
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.ingestDocument(mockFile)).rejects.toThrow('Network error');
    });

    test('handles network errors in queryDocuments', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.queryDocuments('Question?')).rejects.toThrow('Network error');
    });

    test('handles network errors in selectDocuments', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.selectDocuments(['doc1'])).rejects.toThrow('Network error');
    });
  });
});
