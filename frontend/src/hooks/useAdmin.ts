import { useCallback, useEffect, useState } from 'react';

import { apiClient, ApiError } from '../api/client';
import type { AdminStatsResponse, DatabaseInfoResponse, ResetDatabaseResponse } from '../types/document';

interface UseAdminResult {
  stats: AdminStatsResponse | null;
  databaseInfo: DatabaseInfoResponse | null;
  isLoading: boolean;
  isResetting: boolean;
  error: string | null;
  reload: () => Promise<void>;
  resetDatabase: () => Promise<ResetDatabaseResponse>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Admin-Daten konnten nicht geladen werden.';
}

export function useAdmin(): UseAdminResult {
  const [stats, setStats] = useState<AdminStatsResponse | null>(null);
  const [databaseInfo, setDatabaseInfo] = useState<DatabaseInfoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const [nextStats, nextDatabaseInfo] = await Promise.all([apiClient.getAdminStats(), apiClient.getDatabaseInfo()]);
      setStats(nextStats);
      setDatabaseInfo(nextDatabaseInfo);
    } catch (loadError: unknown) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resetDatabase = useCallback(async (): Promise<ResetDatabaseResponse> => {
    setIsResetting(true);
    setError(null);

    try {
      const response = await apiClient.resetDatabase();
      await reload();
      return response;
    } catch (resetError: unknown) {
      const message = getErrorMessage(resetError);
      setError(message);
      throw new Error(message);
    } finally {
      setIsResetting(false);
    }
  }, [reload]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return {
    stats,
    databaseInfo,
    isLoading,
    isResetting,
    error,
    reload,
    resetDatabase,
  };
}
