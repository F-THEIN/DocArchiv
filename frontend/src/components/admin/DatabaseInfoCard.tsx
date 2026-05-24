import { Card, Group, Stack, Table, Text, ThemeIcon, Title } from '@mantine/core';
import { IconDatabase } from '@tabler/icons-react';

import type { DatabaseInfoResponse } from '../../types/document';

interface DatabaseInfoCardProps {
  databaseInfo: DatabaseInfoResponse | null;
  isLoading: boolean;
}

export function DatabaseInfoCard({ databaseInfo, isLoading }: DatabaseInfoCardProps): React.ReactElement {
  return (
    <Card
      withBorder
      radius={16}
      p="lg"
      style={{
        background: 'var(--navy-card)',
        border: '1.5px solid var(--white-15)',
        boxShadow: '0 12px 20px rgba(0, 0, 0, 0.35)',
      }}
    >
      <Stack gap="lg">
        <Group gap="sm" align="center">
          <ThemeIcon size={44} radius={12} variant="filled" style={{ background: 'var(--white-15)', color: 'var(--gold)' }}>
            <IconDatabase size={24} />
          </ThemeIcon>
          <Stack gap={2}>
            <Title order={2} size="h3" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Datenbank-Info
            </Title>
            <Text c="var(--white-70)" size="sm">
              Technische Details zur PostgreSQL-Datenbank.
            </Text>
          </Stack>
        </Group>

        <Stack gap={4}>
          <Text c="var(--white-40)" size="10px" tt="uppercase" style={{ letterSpacing: '0.09em' }}>
            Datenbankgröße
          </Text>
          <Text c="var(--gold)" fw={900} size="xl" style={{ fontFamily: '"Montserrat", sans-serif' }}>
            {isLoading ? '…' : databaseInfo?.database_size ?? 'unbekannt'}
          </Text>
        </Stack>

        <Stack gap="xs">
          <Text c="white" fw={800} style={{ fontFamily: '"Montserrat", sans-serif' }}>
            Tabellen
          </Text>
          <Table withTableBorder withColumnBorders highlightOnHover styles={{ table: { color: 'var(--white-70)' }, th: { color: 'white' } }}>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Name</Table.Th>
                <Table.Th>Zeilen</Table.Th>
                <Table.Th>Größe</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {(databaseInfo?.tables ?? []).map((table) => (
                <Table.Tr key={table.name}>
                  <Table.Td>{table.name}</Table.Td>
                  <Table.Td>{table.row_count}</Table.Td>
                  <Table.Td>{table.size}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Stack>

        <Stack gap={6}>
          <Text c="var(--white-40)" size="10px" tt="uppercase" style={{ letterSpacing: '0.09em' }}>
            Alembic-Revision
          </Text>
          <Text c="var(--white-70)" style={{ fontFamily: 'monospace' }}>
            {databaseInfo?.alembic_revision ?? 'nicht verfügbar'}
          </Text>
          <Text c="var(--white-40)" size="10px" tt="uppercase" style={{ letterSpacing: '0.09em' }}>
            PostgreSQL-Version
          </Text>
          <Text c="var(--white-70)" size="sm">
            {databaseInfo?.postgres_version ?? 'nicht verfügbar'}
          </Text>
        </Stack>
      </Stack>
    </Card>
  );
}
