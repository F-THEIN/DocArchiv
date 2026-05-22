import { Anchor, Badge, Drawer, Group, List, Stack, Text, Title } from '@mantine/core';
import { IconExternalLink } from '@tabler/icons-react';

import type { DocumentSummary } from '../../types/document';

interface DocumentDetailProps {
  document: DocumentSummary | null;
  opened: boolean;
  onClose: () => void;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatOptionalDate(value: string | null): string {
  if (value === null) {
    return 'Nicht gesetzt';
  }

  return new Intl.DateTimeFormat('de-DE').format(new Date(value));
}

export function DocumentDetail({ document, opened, onClose }: DocumentDetailProps): React.ReactElement {
  return (
    <Drawer opened={opened} onClose={onClose} position="right" size="lg" title="Dokumentdetails">
      {document === null ? null : (
        <Stack gap="lg">
          <Stack gap="xs">
            <Title order={2}>{document.title}</Title>
            <Text c="dimmed">{document.original_filename}</Text>
            <Group gap="xs">
              <Badge variant="light">{document.document_type}</Badge>
              <Badge color="gray" variant="outline">
                {formatOptionalDate(document.document_date)}
              </Badge>
            </Group>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4">
              Zusammenfassung
            </Title>
            <Text>{document.summary || 'Keine Zusammenfassung vorhanden.'}</Text>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4">
              Tags
            </Title>
            <Group gap="xs">
              {document.tags.length > 0 ? (
                document.tags.map((tag) => (
                  <Badge key={tag.id} color={tag.color ?? 'blue'} variant="dot">
                    {tag.name}
                  </Badge>
                ))
              ) : (
                <Text c="dimmed">Keine Tags vergeben.</Text>
              )}
            </Group>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4">
              Ablage
            </Title>
            <List spacing="xs">
              <List.Item>
                <Text span fw={600}>
                  Gespeicherter Dateiname:{' '}
                </Text>
                {document.stored_filename}
              </List.Item>
              <List.Item>
                <Text span fw={600}>
                  Nextcloud-Pfad:{' '}
                </Text>
                {document.nextcloud_path}
              </List.Item>
              <List.Item>
                <Anchor href={document.nextcloud_url} target="_blank" rel="noreferrer">
                  <Group gap={6} component="span">
                    In Nextcloud oeffnen
                    <IconExternalLink size={16} />
                  </Group>
                </Anchor>
              </List.Item>
            </List>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4">
              Metadaten
            </Title>
            <Text size="sm" c="dimmed">
              Erstellt: {formatDateTime(document.created_at)}
            </Text>
            <Text size="sm" c="dimmed">
              Aktualisiert: {formatDateTime(document.updated_at)}
            </Text>
          </Stack>
        </Stack>
      )}
    </Drawer>
  );
}
