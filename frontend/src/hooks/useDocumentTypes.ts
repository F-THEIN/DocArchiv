import { useCallback, useEffect, useState } from 'react';

import { apiClient, ApiError } from '../api/client';
import type { DocumentTypeInfo } from '../types/document';

interface UseDocumentTypesResult {
  documentTypes: DocumentTypeInfo[];
  isLoading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Dokumenttypen konnten nicht geladen werden.';
}

export function useDocumentTypes(): UseDocumentTypesResult {
  const [documentTypes, setDocumentTypes] = useState<DocumentTypeInfo[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.listDocumentTypes();
      setDocumentTypes(data);
    } catch (loadError: unknown) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return {
    documentTypes,
    isLoading,
    error,
    reload,
  };
}
