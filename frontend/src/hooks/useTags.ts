import { useCallback, useEffect, useState } from 'react';

import { apiClient, ApiError } from '../api/client';
import type { Tag } from '../types/document';

interface UseTagsResult {
  tags: Tag[];
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

  return 'Tags konnten nicht geladen werden.';
}

export function useTags(): UseTagsResult {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const tagResponse = await apiClient.listTags();
      setTags(tagResponse);
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
    tags,
    isLoading,
    error,
    reload,
  };
}
