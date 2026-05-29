import {
  ActionIcon,
  AppShell as MantineAppShell,
  Box,
  Group,
  SimpleGrid,
  Stack,
  Text,
  Title,
  UnstyledButton,
  useMantineTheme,
} from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import { IconAdjustmentsHorizontal, IconArchive, IconRefresh, IconSearch, IconSettings, IconTags } from '@tabler/icons-react';
import { useMemo, useState } from 'react';

import { useAdmin } from '../../hooks/useAdmin';
import { useCorrespondents } from '../../hooks/useCorrespondents';
import { useDocuments } from '../../hooks/useDocuments';
import { useDocumentTypes } from '../../hooks/useDocumentTypes';
import { useTags } from '../../hooks/useTags';
import { AdminPage } from '../../pages/AdminPage';
import { HomePage } from '../../pages/HomePage';
import type { DocumentSummary, Tag } from '../../types/document';
import { FilterSidebar, type FilterValues } from '../search/FilterSidebar';
import { TagEditModal } from '../tags/TagEditModal';

const NORMAL_HEADER_HEIGHT_BASE = 196;
const NORMAL_HEADER_HEIGHT_SM = 180;
const COMPACT_HEADER_HEIGHT_BASE = 164;
const COMPACT_HEADER_HEIGHT_SM = 148;
const COMPACT_STATS_PADDING = 6;
const COMPACT_MODE_MAX_HEIGHT = 500;
const BOTTOM_NAV_HEIGHT = 72;

export function DocArchivAppShell(): React.ReactElement {
  const [mobileOpened, { toggle: toggleMobile, close: closeMobile }] = useDisclosure(false);
  const [desktopOpened, { toggle: toggleDesktop, close: closeDesktop }] = useDisclosure(true);
  const [selectedDocument, setSelectedDocument] = useState<DocumentSummary | null>(null);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [activeNavItem, setActiveNavItem] = useState<'archiv' | 'suche' | 'tags' | 'filter' | 'admin'>('archiv');
  const theme = useMantineTheme();
  const isMobile = useMediaQuery(`(max-width: ${theme.breakpoints.sm})`);
  const isCompactHeaderMode = useMediaQuery(`(orientation: landscape), (max-height: ${COMPACT_MODE_MAX_HEIGHT}px)`);
  const documentsState = useDocuments();
  const tagsState = useTags();
  const correspondentsState = useCorrespondents();
  const documentTypesState = useDocumentTypes();
  const adminState = useAdmin();
  const refreshLabel = 'Aktualisieren';
  const documentCount = documentsState.pagination?.total ?? documentsState.documents.length;
  const latestUploadMonth = useMemo(() => {
    if (documentsState.documents.length === 0) {
      return '—';
    }

    const latestTimestamp = documentsState.documents.reduce<number>((latest, document) => {
      const timestamp = new Date(document.created_at).getTime();
      return timestamp > latest ? timestamp : latest;
    }, new Date(documentsState.documents[0].created_at).getTime());

    return new Intl.DateTimeFormat('de-DE', { month: 'long', year: 'numeric' }).format(new Date(latestTimestamp));
  }, [documentsState.documents]);

  const filters: FilterValues = {
    selectedTags: documentsState.query.tags ?? [],
    documentTypeId: documentsState.query.document_type_id !== undefined ? String(documentsState.query.document_type_id) : '',
    correspondentId: documentsState.query.correspondent_id !== undefined ? String(documentsState.query.correspondent_id) : '',
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
      document_type_id: nextFilters.documentTypeId ? Number(nextFilters.documentTypeId) : undefined,
      correspondent_id: nextFilters.correspondentId ? Number(nextFilters.correspondentId) : undefined,
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

  function handleFilterNavigation(): void {
    setActiveNavItem('filter');
    if (isMobile) {
      toggleMobile();
      return;
    }
    toggleDesktop();
  }

  function handleMainNavigation(item: 'archiv' | 'suche' | 'tags' | 'admin'): void {
    setActiveNavItem(item);
    closeMobile();
    closeDesktop();
  }

  async function handleAfterDatabaseReset(): Promise<void> {
    setSelectedDocument(null);
    setEditingTag(null);
    await Promise.all([
      documentsState.reload(),
      tagsState.reload(),
      correspondentsState.reload(),
      documentTypesState.reload(),
      adminState.reload(),
    ]);
  }

  return (
    <MantineAppShell
      header={{
        height: {
          base: isCompactHeaderMode ? COMPACT_HEADER_HEIGHT_BASE : NORMAL_HEADER_HEIGHT_BASE,
          sm: isCompactHeaderMode ? COMPACT_HEADER_HEIGHT_SM : NORMAL_HEADER_HEIGHT_SM,
        },
      }}
      navbar={{
        width: 320,
        breakpoint: 'md',
        collapsed: { mobile: !mobileOpened, desktop: !desktopOpened },
      }}
      footer={{ height: 72 }}
      padding="md"
      styles={{
        main: {
          background: 'var(--navy)',
          paddingBottom: `calc(${BOTTOM_NAV_HEIGHT}px + var(--mantine-spacing-md) + env(safe-area-inset-bottom, 0px))`,
        },
        header: {
          background: 'linear-gradient(160deg, #0a1628, #1a3060, #0f2040)',
          borderBottom: '1px solid var(--white-15)',
          color: 'white',
          boxShadow: '0 12px 24px rgba(0, 0, 0, 0.4)',
        },
        navbar: {
          background: 'var(--navy-mid)',
          borderRight: '1px solid var(--white-15)',
        },
        footer: {
          position: 'sticky',
          bottom: 0,
          background: 'linear-gradient(0deg, #08132a, #0f1f3d)',
          borderTop: '1px solid var(--white-15)',
          zIndex: 200,
        },
      }}
    >
      <MantineAppShell.Header>
        <Stack
          h="100%"
          px={{ base: 'sm', sm: 'lg' }}
          py={isCompactHeaderMode ? 'xs' : 'sm'}
          gap={isCompactHeaderMode ? 'xs' : 'sm'}
          justify="space-between"
        >
          <Group justify="space-between" wrap="nowrap" align="center">
            <Title order={1} size="h2" fw={900} style={{ fontFamily: '"Montserrat", sans-serif', letterSpacing: '0.01em' }}>
              <Text span c="white">
                Doc
              </Text>
              <Text span c="var(--gold)">
                Archiv
              </Text>
            </Title>
            <ActionIcon
              variant="subtle"
              aria-label={refreshLabel}
              aria-busy={documentsState.isLoading}
              onClick={() => void documentsState.reload()}
              loading={documentsState.isLoading}
              c="var(--gold)"
            >
              <IconRefresh size={18} />
            </ActionIcon>
          </Group>

          <Group
            wrap="nowrap"
            gap={0}
            style={{
              border: '1px solid var(--white-15)',
              borderRadius: 14,
              background: 'var(--white-15)',
              overflow: 'hidden',
            }}
          >
            <SimpleGrid cols={3} spacing={0} style={{ width: '100%' }}>
              <Stack
                gap={2}
                p={isCompactHeaderMode ? COMPACT_STATS_PADDING : 'xs'}
                ta="center"
                style={{ background: 'rgba(15, 31, 61, 0.55)' }}
              >
                <Text c="var(--gold)" fw={800} size="lg" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                  {documentCount}
                </Text>
                <Text size="10px" c="var(--white-40)" tt="uppercase" style={{ letterSpacing: '0.07em' }}>
                  Anzahl Dokumente
                </Text>
              </Stack>
              <Stack
                gap={2}
                p={isCompactHeaderMode ? COMPACT_STATS_PADDING : 'xs'}
                ta="center"
                style={{ background: 'rgba(15, 31, 61, 0.55)', borderLeft: '1px solid var(--white-15)', borderRight: '1px solid var(--white-15)' }}
              >
                <Text c="var(--gold)" fw={800} size="lg" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                  {tagsState.tags.length}
                </Text>
                <Text size="10px" c="var(--white-40)" tt="uppercase" style={{ letterSpacing: '0.07em' }}>
                  Anzahl Tags
                </Text>
              </Stack>
              <Stack
                gap={2}
                p={isCompactHeaderMode ? COMPACT_STATS_PADDING : 'xs'}
                ta="center"
                style={{ background: 'rgba(15, 31, 61, 0.55)' }}
              >
                <Text c="var(--gold)" fw={800} size="lg" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                  {latestUploadMonth}
                </Text>
                <Text size="10px" c="var(--white-40)" tt="uppercase" style={{ letterSpacing: '0.07em' }}>
                  Letzter Upload
                </Text>
              </Stack>
            </SimpleGrid>
          </Group>
        </Stack>
      </MantineAppShell.Header>

      <MantineAppShell.Navbar p="md">
        <FilterSidebar
          tags={tagsState.tags}
          documentTypes={documentTypesState.documentTypes}
          correspondents={correspondentsState.correspondents}
          isLoading={tagsState.isLoading || documentTypesState.isLoading || correspondentsState.isLoading}
          values={filters}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
          onClose={() => {
            closeMobile();
            closeDesktop();
          }}
        />
      </MantineAppShell.Navbar>

      <MantineAppShell.Main>
        {activeNavItem === 'admin' ? (
          <AdminPage
            stats={adminState.stats}
            databaseInfo={adminState.databaseInfo}
            isLoading={adminState.isLoading}
            isResetting={adminState.isResetting}
            error={adminState.error}
            onReload={adminState.reload}
            onResetDatabase={adminState.resetDatabase}
            onAfterReset={handleAfterDatabaseReset}
          />
        ) : (
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
        )}
      </MantineAppShell.Main>

      <MantineAppShell.Footer px="xs" py={`calc(var(--mantine-spacing-xs) + env(safe-area-inset-bottom, 0px))`}>
        <Group justify="space-around" wrap="nowrap">
          {[
            { key: 'archiv', label: 'Archiv', icon: IconArchive },
            { key: 'suche', label: 'Suche', icon: IconSearch },
            { key: 'tags', label: 'Tags', icon: IconTags },
            { key: 'filter', label: 'Filter', icon: IconAdjustmentsHorizontal },
            { key: 'admin', label: 'Admin', icon: IconSettings },
          ].map((item) => {
            const isActive = activeNavItem === item.key;
            const Icon = item.icon;

            return (
              <UnstyledButton
                key={item.key}
                onClick={() =>
                  item.key === 'filter'
                    ? handleFilterNavigation()
                    : handleMainNavigation(item.key as 'archiv' | 'suche' | 'tags' | 'admin')
                }
                style={{ minWidth: 56 }}
              >
                <Stack align="center" gap={2}>
                  <Box h={2} w={20} style={{ borderRadius: 99, background: isActive ? 'var(--gold)' : 'transparent' }} />
                  <Icon size={16} color={isActive ? '#ffffff' : 'rgba(255,255,255,0.4)'} />
                  <Text
                    size="10px"
                    tt="uppercase"
                    fw={700}
                    c={isActive ? 'white' : 'var(--white-40)'}
                    style={{ fontFamily: '"Montserrat", sans-serif', letterSpacing: '0.07em' }}
                  >
                    {item.label}
                  </Text>
                </Stack>
              </UnstyledButton>
            );
          })}
        </Group>
      </MantineAppShell.Footer>

      <TagEditModal
        tag={editingTag}
        opened={editingTag !== null}
        onClose={handleCloseTagEdit}
        onSaved={() => void handleTagSaved()}
      />
    </MantineAppShell>
  );
}
