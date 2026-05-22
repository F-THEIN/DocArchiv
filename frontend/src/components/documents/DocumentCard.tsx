import { ActionIcon, Badge, Box, Card, Group, Stack, Text, ThemeIcon, Title, Tooltip } from '@mantine/core';
import { IconExternalLink, IconFileText } from '@tabler/icons-react';

import type { DocumentSummary } from '../../types/document';

interface DocumentCardProps {
  document: DocumentSummary;
  onOpen: (document: DocumentSummary) => void;
}

function getTypeVisuals(type: string): { stripe: string; badgeColor: string; tagBackground: string } {
  const normalizedType = type.trim().toLowerCase();

  if (normalizedType === 'antrag') {
    return {
      stripe: 'linear-gradient(90deg, #c0392b, var(--red))',
      badgeColor: 'var(--red)',
      tagBackground: 'rgba(231, 76, 60, 0.2)',
    };
  }

  if (normalizedType === 'bild') {
    return {
      stripe: 'linear-gradient(90deg, #2563be, var(--teal))',
      badgeColor: 'var(--blue)',
      tagBackground: 'rgba(59, 157, 232, 0.2)',
    };
  }

  return {
    stripe: 'linear-gradient(90deg, #b8962e, var(--gold))',
    badgeColor: 'var(--gold)',
    tagBackground: 'rgba(232, 184, 75, 0.2)',
  };
}

function formatDocumentDate(value: string | null): string {
  if (value === null) {
    return 'Ohne Datum';
  }

  return new Intl.DateTimeFormat('de-DE').format(new Date(value));
}

export function DocumentCard({ document, onOpen }: DocumentCardProps): React.ReactElement {
  const typeVisuals = getTypeVisuals(document.document_type);

  return (
    <Card
      withBorder
      radius={16}
      p="lg"
      role="button"
      onClick={() => onOpen(document)}
      style={{
        cursor: 'pointer',
        border: '1.5px solid var(--white-15)',
        background: 'var(--navy-card)',
        boxShadow: '0 12px 20px rgba(0, 0, 0, 0.35)',
        transition: 'transform 0.2s ease, border-color 0.2s ease',
      }}
      styles={{
        root: {
          '&:hover': {
            transform: 'translateY(-3px)',
            borderColor: 'rgba(232, 184, 75, 0.35)',
          },
        },
      }}
    >
      <Box style={{ height: 4, margin: '-16px -16px 14px', borderRadius: '16px 16px 0 0', background: typeVisuals.stripe }} />

      <Stack gap="sm">
        <Group justify="space-between" align="flex-start" gap="md">
          <Group gap="sm" align="flex-start" wrap="nowrap">
            <ThemeIcon size={42} radius={10} variant="filled" style={{ background: 'var(--white-15)', color: 'white' }}>
              <IconFileText size={22} aria-hidden />
            </ThemeIcon>
            <Stack gap={2}>
              <Text c={typeVisuals.badgeColor} fw={800} size="10px" tt="uppercase" style={{ letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif' }}>
                {document.document_type}
              </Text>
              <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif', fontSize: 15, fontWeight: 700 }}>
                {document.title}
              </Title>
              <Text size="11px" c="var(--white-40)" style={{ fontFamily: '"Open Sans", sans-serif' }}>
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
              c="var(--gold)"
            >
              <IconExternalLink size={18} />
            </ActionIcon>
          </Tooltip>
        </Group>

        <Text c="var(--white-70)" style={{ fontFamily: '"Open Sans", sans-serif', fontSize: 13, lineHeight: 1.55 }}>
          {document.summary || 'Keine Zusammenfassung vorhanden.'}
        </Text>

        <Group gap="xs" wrap="nowrap" align="center">
          <Box style={{ height: 1, background: 'var(--white-15)', flex: 1 }} />
          <Box style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--gold)' }} />
          <Box style={{ height: 1, background: 'var(--white-15)', flex: 1 }} />
        </Group>

        <Group gap="xs">
          <Badge
            radius="xl"
            styles={{
              root: {
                background: typeVisuals.tagBackground,
                color: typeVisuals.badgeColor,
                borderRadius: 100,
                fontFamily: '"Montserrat", sans-serif',
                fontSize: 10,
                fontWeight: 700,
                letterSpacing: '0.07em',
                textTransform: 'uppercase',
              },
            }}
          >
            {document.document_type}
          </Badge>

          <Badge
            radius="xl"
            styles={{
              root: {
                background: document.document_date === null ? 'transparent' : 'var(--white-15)',
                border: document.document_date === null ? '1px solid var(--white-15)' : 'none',
                color: document.document_date === null ? 'var(--white-40)' : 'var(--white-70)',
                borderRadius: 100,
                fontFamily: '"Montserrat", sans-serif',
                fontSize: 10,
                fontWeight: 700,
                letterSpacing: '0.07em',
                textTransform: 'uppercase',
              },
            }}
          >
            {formatDocumentDate(document.document_date)}
          </Badge>

          {document.tags.map((tag) => (
            <Badge
              key={tag.id}
              radius="xl"
              styles={{
                root: {
                  background: 'var(--white-15)',
                  color: 'var(--white-70)',
                  borderRadius: 100,
                  fontFamily: '"Montserrat", sans-serif',
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                },
              }}
            >
              {tag.name}
            </Badge>
          ))}
        </Group>
      </Stack>
    </Card>
  );
}
