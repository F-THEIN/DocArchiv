import { Alert, Stack } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';

import { DocumentDetail } from '../components/documents/DocumentDetail';
import { DocumentList } from '../components/documents/DocumentList';
import { SearchBar } from '../components/search/SearchBar';
import { TagCloud } from '../components/tags/TagCloud';
import type { DocumentSummary, Tag } from '../types/document';

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
  onSearch: (query: string) => void;
  onOpenDocument: (document: DocumentSummary) => void;
  onCloseDocument: () => void;
  onPageChange: (page: number) => void;
  onRetryDocuments: () => void;
  onToggleTag: (tagName: string) => void;
  onEditTag: (tag: Tag) => void;
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
  onSearch,
  onOpenDocument,
  onCloseDocument,
  onPageChange,
  onRetryDocuments,
  onToggleTag,
  onEditTag,
}: HomePageProps): React.ReactElement {
  return (
    <Stack gap="lg">
      <SearchBar value={searchValue} onSearch={onSearch} />

      {tagError ? (
        <Alert color="orange" icon={<IconAlertCircle size={18} />} title="Tags konnten nicht geladen werden">
          {tagError}
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

      <DocumentDetail document={selectedDocument} opened={selectedDocument !== null} onClose={onCloseDocument} />
    </Stack>
  );
}
