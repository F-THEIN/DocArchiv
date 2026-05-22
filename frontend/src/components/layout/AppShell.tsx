import {
  ActionIcon,
  AppShell as MantineAppShell,
  Badge,
  Burger,
  Button,
  Group,
  Stack,
  Text,
  Title,
  Tooltip,
  alpha,
  useMantineTheme,
} from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import { IconRefresh } from '@tabler/icons-react';
import { useState } from 'react';

import { useDocuments } from '../../hooks/useDocuments';
import { useTags } from '../../hooks/useTags';
import { HomePage } from '../../pages/HomePage';
import type { DocumentSummary, Tag } from '../../types/document';
import { FilterSidebar, type FilterValues } from '../search/FilterSidebar';
import { TagEditModal } from '../tags/TagEditModal';

export function DocArchivAppShell(): React.ReactElement {
  const [mobileOpened, { toggle: toggleMobile }] = useDisclosure(false);
  const [desktopOpened, { toggle: toggleDesktop }] = useDisclosure(true);
  const [selectedDocument, setSelectedDocument] = useState<DocumentSummary | null>(null);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const theme = useMantineTheme();
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`);
  const documentsState = useDocuments();
  const tagsState = useTags();
  const refreshLabel = 'Aktualisieren';

  const filters: FilterValues = {
    selectedTags: documentsState.query.tags ?? [],
    documentType: documentsState.query.type ?? '',
    dateFrom: documentsState.query.date_from ?? '',
    dateTo: documentsState.query.date_to ?? '',
    sort: documentsState.query.sort ?? 'date_desc',
  };

  function handleSearch(query: string): void {
    documentsState.updateQuery({ q: query });
  }

  function handleFilterChange(nextFilters: FilterValues): void {
    documentsState.updateQuery({
      tags: nextFilters.selectedTags,
      type: nextFilters.documentType || undefined,
      date_from: nextFilters.dateFrom || undefined,
      date_to: nextFilters.dateTo || undefined,
      sort: nextFilters.sort,
    });
  }

  function handleResetFilters(): void {
    documentsState.setQuery({
      page: 1,
      per_page: 25,
      sort: 'date_desc',
    });
  }

  function handleOpenDocument(document: DocumentSummary): void {
    setSelectedDocument(document);
  }

  function handleCloseDocument(): void {
    setSelectedDocument(null);
  }

  function handleToggleTag(tagName: string): void {
    const selectedTags = documentsState.query.tags ?? [];
    const nextTags = selectedTags.includes(tagName)
      ? selectedTags.filter((selectedTag) => selectedTag !== tagName)
      : [...selectedTags, tagName];

    documentsState.updateQuery({ tags: nextTags });
  }

  function handleEditTag(tag: Tag): void {
    setEditingTag(tag);
  }

  function handleCloseTagEdit(): void {
    setEditingTag(null);
  }

  async function handleTagSaved(): Promise<void> {
    setEditingTag(null);
    await tagsState.reload();
    await documentsState.reload();
  }

  return (
    <MantineAppShell
      header={{ height: { base: 96, sm: 72 } }}
      navbar={{
        width: 320,
        breakpoint: 'md',
        collapsed: { mobile: !mobileOpened, desktop: !desktopOpened },
      }}
      padding="lg"
      styles={{
        main: {
          background:
            'radial-gradient(circle at top right, rgba(255, 179, 71, 0.22), transparent 45%), linear-gradient(180deg, #fffaf3 0%, #f8f9ff 100%)',
        },
        header: {
          background: 'linear-gradient(120deg, #ff7a18 0%, #ff5f6d 55%, #7f5af0 100%)',
          borderBottom: 'none',
          color: 'white',
          boxShadow: '0 10px 24px rgba(127, 90, 240, 0.25)',
        },
        navbar: {
          background: alpha('#ffffff', 0.9),
          backdropFilter: 'blur(10px)',
          borderRight: `1px solid ${alpha(theme.colors.orange[4], 0.25)}`,
        },
      }}
    >
      <MantineAppShell.Header>
        <Group h="100%" px={{ base: 'sm', sm: 'lg' }} justify="space-between" wrap="nowrap">
          <Group gap="sm" wrap="nowrap" flex={1} miw={0}>
            <Burger opened={mobileOpened} onClick={toggleMobile} hiddenFrom="md" size="sm" />
            <Burger opened={desktopOpened} onClick={toggleDesktop} visibleFrom="md" size="sm" />
            <Stack gap={0} miw={0}>
              <Group gap="xs">
                <Title order={1} size="h2">
                  DocArchiv
                </Title>
                <Badge variant="filled" color="grape" visibleFrom="xs">
                  Dokument-Archiv
                </Badge>
              </Group>
              <Text size="sm" c="white" visibleFrom="sm" truncate>
                Lebendiger Dokumenten-Index mit schneller Uebersicht
              </Text>
            </Stack>
          </Group>

          {isMobile ? (
            <Tooltip label={refreshLabel} withArrow>
              <ActionIcon
                variant="white"
                color="violet"
                aria-label={refreshLabel}
                aria-busy={documentsState.isLoading}
                onClick={() => void documentsState.reload()}
                loading={documentsState.isLoading}
              >
                <IconRefresh size={16} />
              </ActionIcon>
            </Tooltip>
          ) : (
            <Button
              variant="white"
              color="violet"
              leftSection={<IconRefresh size={16} />}
              aria-busy={documentsState.isLoading}
              onClick={() => void documentsState.reload()}
              loading={documentsState.isLoading}
            >
              {refreshLabel}
            </Button>
          )}
        </Group>
      </MantineAppShell.Header>

      <MantineAppShell.Navbar p="md">
        <FilterSidebar
          tags={tagsState.tags}
          isLoading={tagsState.isLoading}
          values={filters}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
        />
      </MantineAppShell.Navbar>

      <MantineAppShell.Main>
        <HomePage
          documents={documentsState.documents}
          selectedDocument={selectedDocument}
          selectedTags={documentsState.query.tags ?? []}
          isLoadingDocuments={documentsState.isLoading}
          documentError={documentsState.error}
          tagError={tagsState.error}
          pagination={documentsState.pagination}
          searchValue={documentsState.query.q ?? ''}
          tags={tagsState.tags}
          onSearch={handleSearch}
          onOpenDocument={handleOpenDocument}
          onCloseDocument={handleCloseDocument}
          onPageChange={(page) => documentsState.updateQuery({ page })}
          onRetryDocuments={() => void documentsState.reload()}
          onToggleTag={handleToggleTag}
          onEditTag={handleEditTag}
        />
      </MantineAppShell.Main>

      <TagEditModal
        tag={editingTag}
        opened={editingTag !== null}
        onClose={handleCloseTagEdit}
        onSaved={() => void handleTagSaved()}
      />
    </MantineAppShell>
  );
}
