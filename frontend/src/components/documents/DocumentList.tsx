import { Alert, Button, Pagination, Skeleton, Stack, Text } from '@mantine/core';
import { IconAlertCircle, IconInbox } from '@tabler/icons-react';

import type { DocumentSummary, PaginatedResponse } from '../../types/document';
import { DocumentCard } from './DocumentCard';

interface DocumentListProps {
  documents: DocumentSummary[];
  pagination: Omit<PaginatedResponse<DocumentSummary>, 'items'> | null;
  isLoading: boolean;
  error: string | null;
  onOpenDocument: (document: DocumentSummary) => void;
  onPageChange: (page: number) => void;
  onRetry: () => void;
}

export function DocumentList({
  documents,
  pagination,
  isLoading,
  error,
  onOpenDocument,
  onPageChange,
  onRetry,
}: DocumentListProps): React.ReactElement {
  if (isLoading && documents.length === 0) {
    return (
      <Stack gap="md">
        <Skeleton height={180} radius="lg" />
        <Skeleton height={180} radius="lg" />
        <Skeleton height={180} radius="lg" />
      </Stack>
    );
  }

  if (error !== null) {
    return (
      <Alert
        color="red"
        icon={<IconAlertCircle size={18} />}
        title="Dokumente konnten nicht geladen werden"
        styles={{
          root: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
          title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
          message: { color: 'var(--white-70)' },
        }}
      >
        <Stack gap="sm">
          <Text c="var(--white-70)">{error}</Text>
          <Button
            variant="transparent"
            color="red"
            w="fit-content"
            onClick={onRetry}
            styles={{ root: { border: '1px solid var(--white-15)', color: 'var(--white-70)' } }}
          >
            Erneut laden
          </Button>
        </Stack>
      </Alert>
    );
  }

  if (documents.length === 0) {
    return (
      <Alert
        color="gray"
        icon={<IconInbox size={18} />}
        title="Keine Dokumente gefunden"
        styles={{
          root: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
          title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
          message: { color: 'var(--white-70)' },
        }}
      >
        Passe Suche oder Filter an, um Dokumente im Archiv zu finden.
      </Alert>
    );
  }

  return (
    <Stack gap="md">
      {documents.map((document) => (
        <DocumentCard key={document.id} document={document} onOpen={onOpenDocument} />
      ))}

      {pagination !== null && pagination.pages > 1 ? (
        <Pagination
          value={pagination.page}
          total={pagination.pages}
          onChange={onPageChange}
          withEdges
          styles={{
            control: {
              background: 'var(--navy-card)',
              borderColor: 'var(--white-15)',
              color: 'var(--white-70)',
            },
          }}
        />
      ) : null}
    </Stack>
  );
}
