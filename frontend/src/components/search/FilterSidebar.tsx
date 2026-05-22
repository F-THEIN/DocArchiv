import { Badge, Button, Divider, MultiSelect, Paper, Select, Stack, Text, TextInput, Title } from '@mantine/core';
import { IconFilter, IconX } from '@tabler/icons-react';

import type { DocumentSort, Tag } from '../../types/document';

export interface FilterValues {
  selectedTags: string[];
  documentType: string;
  dateFrom: string;
  dateTo: string;
  sort: DocumentSort;
}

interface FilterSidebarProps {
  tags: Tag[];
  isLoading: boolean;
  values: FilterValues;
  onChange: (values: FilterValues) => void;
  onReset: () => void;
}

const sortOptions: Array<{ value: DocumentSort; label: string }> = [
  { value: 'date_desc', label: 'Datum absteigend' },
  { value: 'date_asc', label: 'Datum aufsteigend' },
  { value: 'title_asc', label: 'Titel A-Z' },
  { value: 'title_desc', label: 'Titel Z-A' },
  { value: 'created_desc', label: 'Neueste zuerst' },
];

export function FilterSidebar({ tags, isLoading, values, onChange, onReset }: FilterSidebarProps): React.ReactElement {
  const tagOptions = tags.map((tag) => ({
    value: tag.name,
    label: `${tag.name} (${tag.document_count})`,
  }));

  function patchValues(partialValues: Partial<FilterValues>): void {
    onChange({
      ...values,
      ...partialValues,
    });
  }

  return (
    <Paper
      radius="xl"
      p="md"
      withBorder
      style={{
        borderColor: 'rgba(127, 90, 240, 0.2)',
        background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 244, 255, 0.95) 100%)',
      }}
    >
      <Stack gap="md">
        <Stack gap={2}>
          <Badge variant="light" color="grape" w="fit-content">
            Navigation
          </Badge>
          <Title order={2} size="h3">
            Filter
          </Title>
          <Text size="sm" c="dimmed">
            Suche nach Tags, Typ und Dokumentdatum eingrenzen.
          </Text>
        </Stack>

        <Divider />

        <MultiSelect
          label="Tags"
          placeholder="Tags auswaehlen"
          data={tagOptions}
          searchable
          clearable
          leftSection={<IconFilter size={16} />}
          value={values.selectedTags}
          onChange={(selectedTags) => patchValues({ selectedTags })}
          disabled={isLoading}
        />

        <TextInput
          label="Dokumenttyp"
          placeholder="z. B. rechnung"
          value={values.documentType}
          onChange={(event) => patchValues({ documentType: event.currentTarget.value })}
        />

        <TextInput
          label="Datum von"
          type="date"
          value={values.dateFrom}
          onChange={(event) => patchValues({ dateFrom: event.currentTarget.value })}
        />

        <TextInput
          label="Datum bis"
          type="date"
          value={values.dateTo}
          onChange={(event) => patchValues({ dateTo: event.currentTarget.value })}
        />

        <Select
          label="Sortierung"
          data={sortOptions}
          value={values.sort}
          allowDeselect={false}
          onChange={(sort) => patchValues({ sort: (sort as DocumentSort | null) ?? 'date_desc' })}
        />

        <Button variant="light" color="gray" leftSection={<IconX size={16} />} onClick={onReset}>
          Filter zuruecksetzen
        </Button>
      </Stack>
    </Paper>
  );
}
