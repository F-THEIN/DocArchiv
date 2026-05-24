import { Alert, Button, Group, Stack, Text, Title } from '@mantine/core';
import { IconAlertCircle, IconRefresh, IconSettings } from '@tabler/icons-react';

import { DatabaseInfoCard } from '../components/admin/DatabaseInfoCard';
import { ResetDatabaseCard } from '../components/admin/ResetDatabaseCard';
import { StatsDashboardCard } from '../components/admin/StatsDashboardCard';
import type { AdminStatsResponse, DatabaseInfoResponse, ResetDatabaseResponse } from '../types/document';

interface AdminPageProps {
  stats: AdminStatsResponse | null;
  databaseInfo: DatabaseInfoResponse | null;
  isLoading: boolean;
  isResetting: boolean;
  error: string | null;
  onReload: () => Promise<void>;
  onResetDatabase: () => Promise<ResetDatabaseResponse>;
  onAfterReset: () => Promise<void>;
}

export function AdminPage({
  stats,
  databaseInfo,
  isLoading,
  isResetting,
  error,
  onReload,
  onResetDatabase,
  onAfterReset,
}: AdminPageProps): React.ReactElement {
  return (
    <Stack gap="lg">
      <Group justify="space-between" align="flex-start">
        <Stack gap={4}>
          <Group gap="xs">
            <IconSettings size={22} color="var(--gold)" />
            <Title order={1} size="h2" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Admin
            </Title>
          </Group>
          <Text c="var(--white-70)">Statistiken, technische Datenbankinformationen und Wartungsfunktionen.</Text>
        </Stack>

        <Button variant="subtle" c="var(--gold)" leftSection={<IconRefresh size={18} />} onClick={() => void onReload()} loading={isLoading}>
          Aktualisieren
        </Button>
      </Group>

      {error ? (
        <Alert
          icon={<IconAlertCircle size={18} />}
          title="Admin-Daten konnten nicht geladen werden"
          styles={{
            root: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
            title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
            message: { color: 'var(--white-70)' },
          }}
        >
          <Text c="var(--white-70)">{error}</Text>
        </Alert>
      ) : null}

      <StatsDashboardCard stats={stats} isLoading={isLoading} />
      <DatabaseInfoCard databaseInfo={databaseInfo} isLoading={isLoading} />
      <ResetDatabaseCard isResetting={isResetting} onReset={onResetDatabase} onAfterReset={onAfterReset} />
    </Stack>
  );
}
