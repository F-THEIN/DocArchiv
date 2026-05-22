import { ActionIcon, Badge, Button, Divider, MultiSelect, Select, Stack, Text, TextInput, Title } from '@mantine/core';
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
  onClose?: () => void;
}

const sortOptions: Array<{ value: DocumentSort; label: string }> = [
  { value: 'date_desc', label: 'Datum absteigend' },
  { value: 'date_asc', label: 'Datum aufsteigend' },
  { value: 'title_asc', label: 'Titel A-Z' },
  { value: 'title_desc', label: 'Titel Z-A' },
  { value: 'created_desc', label: 'Neueste zuerst' },
];

const fieldStyles = {
  label: {
    color: 'var(--white-40)',
    textTransform: 'uppercase',
    letterSpacing: '0.07em',
    fontSize: '10px',
    fontFamily: '"Montserrat", sans-serif',
  },
  input: {
    background: 'var(--navy-card)',
    border: '1px solid var(--white-15)',
    color: 'white',
    '&::placeholder': {
      color: 'var(--white-40)',
    },
  },
};

export function FilterSidebar({ tags, isLoading, values, onChange, onReset, onClose }: FilterSidebarProps): React.ReactElement {
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
    <Stack gap="md" style={{ height: '100%' }}>
      <Stack gap={2}>
        <ActionIcon variant="transparent" c="var(--white-70)" aria-label="Filter schliessen" onClick={onClose}>
          <IconX size={18} />
        </ActionIcon>
        <Badge
          w="fit-content"
          styles={{
            root: {
              background: 'var(--white-15)',
              color: 'var(--gold)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              fontFamily: '"Montserrat", sans-serif',
            },
          }}
        >
          Filteroptionen
        </Badge>
        <Title order={2} size="h3" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
          Filter
        </Title>
        <Text size="sm" c="var(--white-70)">
          Suche nach Tags, Typ und Dokumentdatum eingrenzen.
        </Text>
      </Stack>

      <Divider color="var(--white-15)" />

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
        styles={{
          ...fieldStyles,
          dropdown: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
          option: { color: 'var(--white-70)' },
          pill: { background: 'var(--white-15)', color: 'var(--white-70)' },
        }}
      />

      <TextInput
        label="Dokumenttyp"
        placeholder="z. B. rechnung"
        value={values.documentType}
        onChange={(event) => patchValues({ documentType: event.currentTarget.value })}
        styles={fieldStyles}
      />

      <TextInput
        label="Datum von"
        type="date"
        value={values.dateFrom}
        onChange={(event) => patchValues({ dateFrom: event.currentTarget.value })}
        styles={fieldStyles}
      />

      <TextInput
        label="Datum bis"
        type="date"
        value={values.dateTo}
        onChange={(event) => patchValues({ dateTo: event.currentTarget.value })}
        styles={fieldStyles}
      />

      <Select
        label="Sortierung"
        data={sortOptions}
        value={values.sort}
        allowDeselect={false}
        onChange={(sort) => patchValues({ sort: (sort as DocumentSort | null) ?? 'date_desc' })}
        styles={{
          ...fieldStyles,
          dropdown: { background: 'var(--navy-card)', border: '1px solid var(--white-15)' },
          option: { color: 'var(--white-70)' },
        }}
      />

      <Button
        variant="transparent"
        leftSection={<IconX size={16} />}
        onClick={onReset}
        styles={{
          root: {
            border: '1px solid var(--white-15)',
            color: 'var(--white-40)',
            fontFamily: '"Montserrat", sans-serif',
            fontWeight: 700,
          },
        }}
      >
        Filter zuruecksetzen
      </Button>
    </Stack>
  );
}
