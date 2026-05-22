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
        <Skeleton height={132} radius="lg" />
        <Skeleton height={132} radius="lg" />
        <Skeleton height={132} radius="lg" />
      </Stack>
    );
  }

  if (error !== null) {
    return (
      <Alert color="red" icon={<IconAlertCircle size={18} />} title="Dokumente konnten nicht geladen werden">
        <Stack gap="sm">
          <Text>{error}</Text>
          <Button variant="light" color="red" w="fit-content" onClick={onRetry}>
            Erneut laden
          </Button>
        </Stack>
      </Alert>
    );
  }

  if (documents.length === 0) {
    return (
      <Alert color="gray" icon={<IconInbox size={18} />} title="Keine Dokumente gefunden">
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
        <Pagination value={pagination.page} total={pagination.pages} onChange={onPageChange} withEdges />
      ) : null}
    </Stack>
  );
}
