import { useCallback, useEffect, useMemo, useState } from 'react';

import { apiClient, ApiError } from '../api/client';
import type { DocumentListQuery, DocumentSummary, PaginatedResponse, UpdateDocumentPayload } from '../types/document';

interface UseDocumentsResult {
  documents: DocumentSummary[];
  pagination: Omit<PaginatedResponse<DocumentSummary>, 'items'> | null;
  isLoading: boolean;
  error: string | null;
  query: DocumentListQuery;
  setQuery: (query: DocumentListQuery) => void;
  updateQuery: (partialQuery: Partial<DocumentListQuery>) => void;
  reload: () => Promise<void>;
  updateDocument: (id: number, payload: UpdateDocumentPayload) => Promise<DocumentSummary>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Dokumente konnten nicht geladen werden.';
}

export function useDocuments(initialQuery: DocumentListQuery = {}): UseDocumentsResult {
  const [query, setQuery] = useState<DocumentListQuery>({
    page: 1,
    per_page: 25,
    sort: 'date_desc',
    ...initialQuery,
  });
  const [response, setResponse] = useState<PaginatedResponse<DocumentSummary> | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const documentsResponse = await apiClient.listDocuments(query);
      setResponse(documentsResponse);
    } catch (loadError: unknown) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const updateQuery = useCallback((partialQuery: Partial<DocumentListQuery>): void => {
    setQuery((currentQuery) => ({
      ...currentQuery,
      ...partialQuery,
      page: partialQuery.page ?? 1,
    }));
  }, []);

  const pagination = useMemo<Omit<PaginatedResponse<DocumentSummary>, 'items'> | null>(() => {
    if (response === null) {
      return null;
    }

    return {
      total: response.total,
      page: response.page,
      per_page: response.per_page,
      pages: response.pages,
    };
  }, [response]);

  const updateDocument = useCallback(async (id: number, payload: UpdateDocumentPayload): Promise<DocumentSummary> => {
    const updated = await apiClient.updateDocument(id, payload);
    await reload();
    return updated;
  }, [reload]);

  return {
    documents: response?.items ?? [],
    pagination,
    isLoading,
    error,
    query,
    setQuery,
    updateQuery,
    reload,
    updateDocument,
  };
}
