import { Alert, Group, Paper, Stack, Text, ThemeIcon, Title } from '@mantine/core';
import { IconAlertCircle, IconSparkles } from '@tabler/icons-react';

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
      <Paper
        withBorder
        radius="xl"
        p="lg"
        style={{
          borderColor: 'rgba(255, 122, 24, 0.22)',
          background:
            'linear-gradient(120deg, rgba(255, 122, 24, 0.12) 0%, rgba(255, 95, 109, 0.12) 50%, rgba(127, 90, 240, 0.15) 100%)',
        }}
      >
        <Group wrap="nowrap" align="flex-start" gap="md">
          <ThemeIcon size={44} radius="xl" variant="gradient" gradient={{ from: 'orange.5', to: 'grape.6', deg: 130 }}>
            <IconSparkles size={22} />
          </ThemeIcon>
          <Stack gap={2}>
            <Title order={2}>Willkommen im Archiv</Title>
            <Text c="dimmed">
              Entdecke Dokumente schneller mit farbigen Filtern, klaren Karten und direktem Zugriff auf Nextcloud.
            </Text>
          </Stack>
        </Group>
      </Paper>

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
