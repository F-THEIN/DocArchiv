import { ActionIcon, Badge, Card, Group, Stack, Text, Title, Tooltip } from '@mantine/core';
import { IconExternalLink, IconFileText } from '@tabler/icons-react';

import type { DocumentSummary } from '../../types/document';

interface DocumentCardProps {
  document: DocumentSummary;
  onOpen: (document: DocumentSummary) => void;
}

function formatDocumentDate(value: string | null): string {
  if (value === null) {
    return 'Ohne Datum';
  }

  return new Intl.DateTimeFormat('de-DE').format(new Date(value));
}

export function DocumentCard({ document, onOpen }: DocumentCardProps): React.ReactElement {
  return (
    <Card withBorder radius="lg" shadow="xs" p="lg" role="button" onClick={() => onOpen(document)}>
      <Stack gap="sm">
        <Group justify="space-between" align="flex-start" gap="md">
          <Group gap="sm" align="flex-start" wrap="nowrap">
            <IconFileText size={24} aria-hidden />
            <Stack gap={2}>
              <Title order={3} size="h4">
                {document.title}
              </Title>
              <Text size="sm" c="dimmed">
                {document.original_filename}
              </Text>
            </Stack>
          </Group>

          <Tooltip label="In Nextcloud oeffnen">
            <ActionIcon
              component="a"
              href={document.nextcloud_url}
              target="_blank"
              rel="noreferrer"
              variant="subtle"
              aria-label="Dokument in Nextcloud oeffnen"
              onClick={(event) => event.stopPropagation()}
            >
              <IconExternalLink size={18} />
            </ActionIcon>
          </Tooltip>
        </Group>

        <Text lineClamp={2}>{document.summary || 'Keine Zusammenfassung vorhanden.'}</Text>

        <Group gap="xs">
          <Badge variant="light">{document.document_type}</Badge>
          <Badge variant="outline" color="gray">
            {formatDocumentDate(document.document_date)}
          </Badge>
          {document.tags.map((tag) => (
            <Badge key={tag.id} color={tag.color ?? 'blue'} variant="dot">
              {tag.name}
            </Badge>
          ))}
        </Group>
      </Stack>
    </Card>
  );
}
