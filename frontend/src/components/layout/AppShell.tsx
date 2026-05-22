import {
  Alert,
  AppShell as MantineAppShell,
  Badge,
  Burger,
  Button,
  Group,
  Loader,
  Paper,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconAlertCircle, IconRefresh } from '@tabler/icons-react';

import { useDocuments } from '../../hooks/useDocuments';
import { useTags } from '../../hooks/useTags';
import { FilterSidebar, type FilterValues } from '../search/FilterSidebar';
import { SearchBar } from '../search/SearchBar';

export function DocArchivAppShell(): React.ReactElement {
  const [mobileOpened, { toggle: toggleMobile }] = useDisclosure(false);
  const [desktopOpened, { toggle: toggleDesktop }] = useDisclosure(true);
  const documentsState = useDocuments();
  const tagsState = useTags();

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

  return (
    <MantineAppShell
      header={{ height: 72 }}
      navbar={{
        width: 320,
        breakpoint: 'md',
        collapsed: { mobile: !mobileOpened, desktop: !desktopOpened },
      }}
      padding="lg"
    >
      <MantineAppShell.Header>
        <Group h="100%" px="lg" justify="space-between">
          <Group gap="md">
            <Burger opened={mobileOpened} onClick={toggleMobile} hiddenFrom="md" size="sm" />
            <Burger opened={desktopOpened} onClick={toggleDesktop} visibleFrom="md" size="sm" />
            <Stack gap={0}>
              <Group gap="xs">
                <Title order={1} size="h2">
                  DocArchiv
                </Title>
                <Badge variant="light">SPA</Badge>
              </Group>
              <Text size="sm" c="dimmed">
                Durchsuchbarer Index fuer gescannte Dokumente
              </Text>
            </Stack>
          </Group>

          <Button
            variant="light"
            leftSection={<IconRefresh size={16} />}
            onClick={() => void documentsState.reload()}
            loading={documentsState.isLoading}
          >
            Aktualisieren
          </Button>
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
        <Stack gap="lg">
          <SearchBar value={documentsState.query.q ?? ''} onSearch={handleSearch} />

          {documentsState.error ? (
            <Alert color="red" icon={<IconAlertCircle size={18} />} title="Dokumente konnten nicht geladen werden">
              {documentsState.error}
            </Alert>
          ) : null}

          {tagsState.error ? (
            <Alert color="orange" icon={<IconAlertCircle size={18} />} title="Tags konnten nicht geladen werden">
              {tagsState.error}
            </Alert>
          ) : null}

          <Paper withBorder radius="lg" p="xl">
            <Stack align="center" gap="sm" py="xl">
              {documentsState.isLoading ? <Loader /> : null}
              <Title order={2} size="h3">
                Dokumentliste wird im naechsten Schritt angebunden
              </Title>
              <Text c="dimmed" ta="center" maw={620}>
                Suche, Filter und API-Hooks sind vorbereitet. Aktuell wurden {documentsState.documents.length}{' '}
                Dokumente aus der API-Antwort geladen.
              </Text>
              {documentsState.pagination ? (
                <Text size="sm" c="dimmed">
                  Seite {documentsState.pagination.page} von {documentsState.pagination.pages} ·{' '}
                  {documentsState.pagination.total} Treffer
                </Text>
              ) : null}
            </Stack>
          </Paper>
        </Stack>
      </MantineAppShell.Main>
    </MantineAppShell>
  );
}
