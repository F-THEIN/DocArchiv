import { useCallback, useEffect, useState } from 'react';

import { apiClient, ApiError } from '../api/client';
import type { Correspondent } from '../types/document';

interface UseCorrespondentsResult {
  correspondents: Correspondent[];
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

  return 'Korrespondenten konnten nicht geladen werden.';
}

export function useCorrespondents(): UseCorrespondentsResult {
  const [correspondents, setCorrespondents] = useState<Correspondent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.listCorrespondents();
      setCorrespondents(data);
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
    correspondents,
    isLoading,
    error,
    reload,
  };
}
