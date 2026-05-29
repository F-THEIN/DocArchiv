import { Anchor, Badge, Drawer, Group, List, Stack, Text, Title } from '@mantine/core';
import { IconExternalLink, IconUser } from '@tabler/icons-react';

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
    <Drawer
      opened={opened}
      onClose={onClose}
      position="right"
      size="lg"
      title="Dokumentdetails"
      styles={{
        content: { background: 'var(--navy-mid)', color: 'white' },
        header: { background: 'var(--navy-mid)', borderBottom: '1px solid var(--white-15)' },
        title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
        close: { color: 'var(--white-70)' },
      }}
    >
      {document === null ? null : (
        <Stack gap="lg">
          <Stack gap="xs">
            <Title order={2} c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              {document.title}
            </Title>
            <Text c="var(--white-40)">{document.original_filename}</Text>
            <Group gap="xs">
              <Badge styles={{ root: { background: 'var(--white-15)', color: 'var(--white-70)' } }}>{document.document_type.name}</Badge>
              <Badge styles={{ root: { borderColor: 'var(--white-15)', color: 'var(--white-40)' } }} variant="outline">
                {formatOptionalDate(document.document_date)}
              </Badge>
            </Group>
          </Stack>

          {document.correspondent !== null ? (
            <Stack gap="xs">
              <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                Korrespondent
              </Title>
              <Group gap="xs">
                <IconUser size={16} color="var(--blue)" />
                <Text c="var(--white-70)">{document.correspondent.name}</Text>
              </Group>
            </Stack>
          ) : null}

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Zusammenfassung
            </Title>
            <Text c="var(--white-70)">{document.summary || 'Keine Zusammenfassung vorhanden.'}</Text>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Tags
            </Title>
            <Group gap="xs">
              {document.tags.length > 0 ? (
                document.tags.map((tag) => (
                  <Badge key={tag.id} styles={{ root: { background: 'var(--white-15)', color: 'var(--white-70)' } }}>
                    {tag.name}
                  </Badge>
                ))
              ) : (
                <Text c="var(--white-40)">Keine Tags vergeben.</Text>
              )}
            </Group>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Ablage
            </Title>
            <List spacing="xs">
              <List.Item>
                <Text span fw={600} c="var(--white-70)">
                  Gespeicherter Dateiname:{' '}
                </Text>
                <Text span c="var(--white-40)">
                  {document.stored_filename}
                </Text>
              </List.Item>
              <List.Item>
                <Text span fw={600} c="var(--white-70)">
                  Nextcloud-Pfad:{' '}
                </Text>
                <Text span c="var(--white-40)">
                  {document.nextcloud_path}
                </Text>
              </List.Item>
              <List.Item>
                <Anchor href={document.nextcloud_url} target="_blank" rel="noreferrer" c="var(--gold)">
                  <Group gap={6} component="span">
                    In Nextcloud oeffnen
                    <IconExternalLink size={16} />
                  </Group>
                </Anchor>
              </List.Item>
            </List>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Metadaten
            </Title>
            <Text size="sm" c="var(--white-40)">
              Erstellt: {formatDateTime(document.created_at)}
            </Text>
            <Text size="sm" c="var(--white-40)">
              Aktualisiert: {formatDateTime(document.updated_at)}
            </Text>
          </Stack>
        </Stack>
      )}
    </Drawer>
  );
}
