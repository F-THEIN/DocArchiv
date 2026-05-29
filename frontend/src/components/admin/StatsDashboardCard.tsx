import { Box, Card, Group, SimpleGrid, Stack, Table, Text, ThemeIcon, Title } from '@mantine/core';
import { IconChartBar, IconFileText, IconTags, IconUser } from '@tabler/icons-react';

import type { AdminStatsResponse } from '../../types/document';

interface StatsDashboardCardProps {
  stats: AdminStatsResponse | null;
  isLoading: boolean;
}

function formatMonth(value: string): string {
  const [year, month] = value.split('-');
  if (year === undefined || month === undefined) {
    return value;
  }

  return new Intl.DateTimeFormat('de-DE', { month: 'long', year: 'numeric' }).format(new Date(Number(year), Number(month) - 1, 1));
}

function StatTile({ label, value, tone }: { label: string; value: number | string; tone?: 'gold' | 'red' | 'blue' }): React.ReactElement {
  const color = tone === 'red' ? 'var(--red)' : tone === 'blue' ? 'var(--blue)' : 'var(--gold)';

  return (
    <Stack gap={4} p="md" style={{ border: '1px solid var(--white-15)', borderRadius: 14, background: 'rgba(255, 255, 255, 0.04)' }}>
      <Text c={color} fw={900} size="xl" style={{ fontFamily: '"Montserrat", sans-serif' }}>
        {value}
      </Text>
      <Text size="10px" c="var(--white-40)" tt="uppercase" style={{ letterSpacing: '0.09em' }}>
        {label}
      </Text>
    </Stack>
  );
}

export function StatsDashboardCard({ stats, isLoading }: StatsDashboardCardProps): React.ReactElement {
  const maxTagCount = Math.max(...(stats?.top_tags.map((tag) => tag.count) ?? [1]), 1);
  const maxCorrespondentCount = Math.max(...(stats?.top_correspondents.map((c) => c.count) ?? [1]), 1);

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
            <IconChartBar size={24} />
          </ThemeIcon>
          <Stack gap={2}>
            <Title order={2} size="h3" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Statistik-Dashboard
            </Title>
            <Text c="var(--white-70)" size="sm">
              Kennzahlen zu Dokumenten, Tags, Korrespondenten und Verteilungen.
            </Text>
          </Stack>
        </Group>

        <SimpleGrid cols={{ base: 2, xs: 3, md: 6 }} spacing="sm">
          <StatTile label="Dokumente" value={isLoading ? '…' : stats?.total_documents ?? 0} />
          <StatTile label="Tags" value={isLoading ? '…' : stats?.total_tags ?? 0} tone="blue" />
          <StatTile label="Korrespondenten" value={isLoading ? '…' : stats?.total_correspondents ?? 0} tone="blue" />
          <StatTile label="Dokumenttypen" value={isLoading ? '…' : stats?.total_document_types ?? 0} tone="blue" />
          <StatTile label="Ohne Tags" value={isLoading ? '…' : stats?.documents_without_tags ?? 0} tone="red" />
          <StatTile label="Ohne Korrespondent" value={isLoading ? '…' : stats?.documents_without_correspondent ?? 0} tone="red" />
        </SimpleGrid>

        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
          {/* Dokumente pro Typ */}
          <Stack gap="sm">
            <Group gap="xs">
              <IconFileText size={18} color="var(--gold)" />
              <Text c="white" fw={800} style={{ fontFamily: '"Montserrat", sans-serif' }}>
                Dokumente pro Typ
              </Text>
            </Group>
            <Table highlightOnHover withTableBorder withColumnBorders styles={{ table: { color: 'var(--white-70)' }, th: { color: 'white' } }}>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Typ</Table.Th>
                  <Table.Th>Anzahl</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {(stats?.documents_by_type ?? []).map((typeCount) => (
                  <Table.Tr key={typeCount.name}>
                    <Table.Td>{typeCount.name}</Table.Td>
                    <Table.Td>{typeCount.count}</Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Stack>

          {/* Top-Tags */}
          <Stack gap="sm">
            <Group gap="xs">
              <IconTags size={18} color="var(--gold)" />
              <Text c="white" fw={800} style={{ fontFamily: '"Montserrat", sans-serif' }}>
                Top-Tags
              </Text>
            </Group>
            <Stack gap="xs">
              {(stats?.top_tags ?? []).map((tag) => (
                <Stack key={tag.name} gap={4}>
                  <Group justify="space-between" wrap="nowrap">
                    <Text c="var(--white-70)" size="sm">
                      {tag.name}
                    </Text>
                    <Text c="var(--gold)" size="sm" fw={800}>
                      {tag.count}
                    </Text>
                  </Group>
                  <Box style={{ height: 8, borderRadius: 999, background: 'var(--white-15)', overflow: 'hidden' }}>
                    <Box style={{ width: `${Math.round((tag.count / maxTagCount) * 100)}%`, height: '100%', background: 'var(--gold)' }} />
                  </Box>
                </Stack>
              ))}
              {stats !== null && stats.top_tags.length === 0 ? <Text c="var(--white-40)">Noch keine Tags vorhanden.</Text> : null}
            </Stack>
          </Stack>
        </SimpleGrid>

        {/* Top-Korrespondenten */}
        <Stack gap="sm">
          <Group gap="xs">
            <IconUser size={18} color="var(--blue)" />
            <Text c="white" fw={800} style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Top-Korrespondenten
            </Text>
          </Group>
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
            <Stack gap="xs">
              {(stats?.top_correspondents ?? []).map((correspondent) => (
                <Stack key={correspondent.name} gap={4}>
                  <Group justify="space-between" wrap="nowrap">
                    <Text c="var(--white-70)" size="sm">
                      {correspondent.name}
                    </Text>
                    <Text c="var(--blue)" size="sm" fw={800}>
                      {correspondent.count}
                    </Text>
                  </Group>
                  <Box style={{ height: 8, borderRadius: 999, background: 'var(--white-15)', overflow: 'hidden' }}>
                    <Box style={{ width: `${Math.round((correspondent.count / maxCorrespondentCount) * 100)}%`, height: '100%', background: 'var(--blue)' }} />
                  </Box>
                </Stack>
              ))}
              {stats !== null && stats.top_correspondents.length === 0 ? <Text c="var(--white-40)">Noch keine Korrespondenten vorhanden.</Text> : null}
            </Stack>
          </SimpleGrid>
        </Stack>

        {/* Dokumente pro Monat */}
        <Stack gap="sm">
          <Text c="white" fw={800} style={{ fontFamily: '"Montserrat", sans-serif' }}>
            Dokumente pro Monat
          </Text>
          <Table withTableBorder withColumnBorders styles={{ table: { color: 'var(--white-70)' }, th: { color: 'white' } }}>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Monat</Table.Th>
                <Table.Th>Anzahl</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {(stats?.documents_by_month ?? []).map((item) => (
                <Table.Tr key={item.month}>
                  <Table.Td>{formatMonth(item.month)}</Table.Td>
                  <Table.Td>{item.count}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Stack>
      </Stack>
    </Card>
  );
}
