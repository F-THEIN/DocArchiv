import { Alert, Stack, Text } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

import { DocumentDetail } from '../components/documents/DocumentDetail';
import { DocumentList } from '../components/documents/DocumentList';
import { SearchBar } from '../components/search/SearchBar';
import { TagCloud } from '../components/tags/TagCloud';
import type { Correspondent, DocumentSummary, DocumentTypeInfo, Tag, UpdateDocumentPayload } from '../types/document';

interface HomePageProps {
  documents: DocumentSummary[];
  selectedDocument: DocumentSummary | null;
  selectedTags: string[];
  isLoadingDocuments: boolean;
  documentError: string | null;
  tagError: string | null;
  pagination: Parameters<typeof DocumentList>[0]['pagination'];
  searchValue: string;
  tags: Parameters<typeof TagCloud>[0]['tags'];
  correspondents: Correspondent[];
  documentTypes: DocumentTypeInfo[];
  onSearch: (query: string) => void;
  onOpenDocument: (document: DocumentSummary) => void;
  onCloseDocument: () => void;
  onPageChange: (page: number) => void;
  onRetryDocuments: () => void;
  onToggleTag: (tagName: string) => void;
  onEditTag: (tag: Tag) => void;
  onUpdateDocument: (id: number, payload: UpdateDocumentPayload) => Promise<DocumentSummary>;
}

export function HomePage({
  documents,
  selectedDocument,
  selectedTags,
  isLoadingDocuments,
  documentError,
  tagError,
  pagination,
  searchValue,
  tags,
  correspondents,
  documentTypes,
  onSearch,
  onOpenDocument,
  onCloseDocument,
  onPageChange,
  onRetryDocuments,
  onToggleTag,
  onEditTag,
  onUpdateDocument,
}: HomePageProps): React.ReactElement {
  return (
    <Stack gap="lg">
      <SearchBar value={searchValue} onSearch={onSearch} />

      {tagError ? (
        <Alert
          icon={<IconAlertCircle size={18} />}
          title="Tags konnten nicht geladen werden"
          styles={{
            root: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
            title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
            message: { color: 'var(--white-70)' },
          }}
        >
          <Text c="var(--white-70)">{tagError}</Text>
        </Alert>
      ) : null}

      <TagCloud tags={tags} selectedTags={selectedTags} onToggleTag={onToggleTag} onEditTag={onEditTag} />

      <DocumentList
        documents={documents}
        pagination={pagination}
        isLoading={isLoadingDocuments}
        error={documentError}
        onOpenDocument={onOpenDocument}
        onPageChange={onPageChange}
        onRetry={onRetryDocuments}
      />

      <DocumentDetail
        document={selectedDocument}
        opened={selectedDocument !== null}
        correspondents={correspondents}
        documentTypes={documentTypes}
        tags={tags}
        onClose={onCloseDocument}
        onUpdate={onUpdateDocument}
      />
    </Stack>
  );
}
