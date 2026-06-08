import { Alert, Badge, Button, Card, Checkbox, Group, ScrollArea, Stack, Text, ThemeIcon, Title } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconAlertCircle, IconArrowMergeRight, IconCheck } from '@tabler/icons-react';
import { useState } from 'react';

import { apiClient, ApiError } from '../../api/client';
import type { Correspondent } from '../../types/document';

interface MergeCorrespondentsCardProps {
  correspondents: Correspondent[];
  onAfterMerge: () => Promise<void>;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Korrespondenten konnten nicht zusammengefuehrt werden.';
}

export function MergeCorrespondentsCard({ correspondents, onAfterMerge }: MergeCorrespondentsCardProps): React.ReactElement {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [targetId, setTargetId] = useState<number | null>(null);
  const [isMerging, setIsMerging] = useState(false);
  const [mergeError, setMergeError] = useState<string | null>(null);

  const selectedCorrespondents = correspondents.filter((c) => selectedIds.includes(c.id));
  const canMerge = selectedIds.length >= 2 && targetId !== null;

  function handleToggle(id: number): void {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id],
    );
    if (targetId === id) {
      setTargetId(null);
    }
  }

  function handleSetTarget(id: number): void {
    setTargetId(id);
  }

  async function handleMerge(): Promise<void> {
    if (targetId === null) return;

    const sourceIds = selectedIds.filter((id) => id !== targetId);
    if (sourceIds.length === 0) return;

    setIsMerging(true);
    setMergeError(null);

    try {
      const result = await apiClient.mergeCorrespondents({
        source_ids: sourceIds,
        target_id: targetId,
      });
      notifications.show({
        title: 'Korrespondenten zusammengefuehrt',
        message: `${result.merged_count} Korrespondent(en) entfernt, ${result.documents_moved} Dokument(e) umgehaengt auf "${result.target.name}".`,
        color: 'green',
      });
      setSelectedIds([]);
      setTargetId(null);
      await onAfterMerge();
    } catch (error: unknown) {
      setMergeError(getErrorMessage(error));
    } finally {
      setIsMerging(false);
    }
  }

  return (
    <Card
      withBorder
      radius={16}
      p="lg"
      style={{
        background: 'linear-gradient(145deg, rgba(52, 152, 219, 0.10), var(--navy-card))',
        border: '1.5px solid var(--white-15)',
        boxShadow: '0 12px 20px rgba(0, 0, 0, 0.35)',
      }}
    >
      <Stack gap="md">
        <Group gap="sm" align="flex-start" wrap="nowrap">
          <ThemeIcon size={44} radius={12} variant="filled" style={{ background: 'rgba(52, 152, 219, 0.22)', color: 'var(--blue)' }}>
            <IconArrowMergeRight size={24} />
          </ThemeIcon>
          <Stack gap={4}>
            <Text c="var(--blue)" fw={800} size="10px" tt="uppercase" style={{ letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif' }}>
              Datenpflege
            </Text>
            <Title order={2} size="h3" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Korrespondenten zusammenfuehren
            </Title>
            <Text c="var(--white-70)" size="sm">
              Waehle Duplikate aus, bestimme das Ziel und fuehre sie zusammen. Alle Dokumente werden dem Ziel zugeordnet.
            </Text>
          </Stack>
        </Group>

        <ScrollArea.Autosize mah={320}>
          <Stack gap={6}>
            {correspondents.map((c) => {
              const isSelected = selectedIds.includes(c.id);
              const isTarget = targetId === c.id;

              return (
                <Group
                  key={c.id}
                  gap="sm"
                  wrap="nowrap"
                  p="xs"
                  style={{
                    borderRadius: 8,
                    background: isTarget ? 'rgba(52, 152, 219, 0.15)' : isSelected ? 'var(--white-15)' : 'transparent',
                    border: isTarget ? '1px solid rgba(52, 152, 219, 0.5)' : '1px solid transparent',
                  }}
                >
                  <Checkbox
                    checked={isSelected}
                    onChange={() => handleToggle(c.id)}
                    styles={{ input: { background: 'var(--navy-card)', borderColor: 'var(--white-15)' } }}
                  />
                  <Text c="white" size="sm" style={{ flex: 1 }}>
                    {c.name}
                  </Text>
                  <Badge size="sm" styles={{ root: { background: 'var(--white-15)', color: 'var(--white-70)' } }}>
                    {c.document_count}
                  </Badge>
                  {isSelected ? (
                    <Button
                      size="compact-xs"
                      variant={isTarget ? 'filled' : 'subtle'}
                      onClick={() => handleSetTarget(c.id)}
                      leftSection={isTarget ? <IconCheck size={12} /> : undefined}
                      styles={{
                        root: isTarget
                          ? { background: 'var(--blue)', color: 'white' }
                          : { color: 'var(--white-40)' },
                      }}
                    >
                      Ziel
                    </Button>
                  ) : null}
                </Group>
              );
            })}
          </Stack>
        </ScrollArea.Autosize>

        {selectedIds.length >= 2 && targetId === null ? (
          <Alert
            icon={<IconAlertCircle size={18} />}
            styles={{
              root: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
              title: { color: 'white' },
              message: { color: 'var(--white-70)' },
            }}
          >
            Waehle einen der markierten Korrespondenten als Ziel aus.
          </Alert>
        ) : null}

        {mergeError !== null ? (
          <Alert
            icon={<IconAlertCircle size={18} />}
            title="Fehler"
            styles={{
              root: { background: 'var(--navy-card)', border: '1px solid var(--mantine-color-red-8)' },
              title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
              message: { color: 'var(--white-70)' },
            }}
          >
            {mergeError}
          </Alert>
        ) : null}

        {canMerge ? (
          <Text size="sm" c="var(--white-70)">
            {selectedCorrespondents.filter((c) => c.id !== targetId).map((c) => c.name).join(', ')}
            {' → '}
            <Text span fw={700} c="white">{selectedCorrespondents.find((c) => c.id === targetId)?.name}</Text>
          </Text>
        ) : null}

        <Group justify="flex-end">
          {selectedIds.length > 0 ? (
            <Button
              variant="subtle"
              onClick={() => { setSelectedIds([]); setTargetId(null); }}
              disabled={isMerging}
              styles={{ root: { color: 'var(--white-40)' } }}
            >
              Auswahl aufheben
            </Button>
          ) : null}
          <Button
            leftSection={<IconArrowMergeRight size={18} />}
            onClick={() => void handleMerge()}
            disabled={!canMerge}
            loading={isMerging}
            styles={{ root: { background: 'var(--gold)', color: 'var(--navy)', fontFamily: '"Montserrat", sans-serif', fontWeight: 700 } }}
          >
            Zusammenfuehren
          </Button>
        </Group>
      </Stack>
    </Card>
  );
}
