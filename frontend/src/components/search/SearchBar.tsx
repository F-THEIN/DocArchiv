import { Button, Group, Paper, TextInput } from '@mantine/core';
import { IconSearch, IconX } from '@tabler/icons-react';
import { useEffect, useState } from 'react';

interface SearchBarProps {
  value: string;
  onSearch: (value: string) => void;
}

export function SearchBar({ value, onSearch }: SearchBarProps): React.ReactElement {
  const [draftValue, setDraftValue] = useState<string>(value);

  useEffect(() => {
    setDraftValue(value);
  }, [value]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    onSearch(draftValue.trim());
  }

  function handleClear(): void {
    setDraftValue('');
    onSearch('');
  }

  return (
    <Paper component="form" withBorder radius="lg" p="md" onSubmit={handleSubmit}>
      <Group align="flex-end" gap="sm">
        <TextInput
          flex={1}
          label="Volltextsuche"
          placeholder="Titel, Zusammenfassung oder Dateiname suchen"
          leftSection={<IconSearch size={18} />}
          value={draftValue}
          onChange={(event) => setDraftValue(event.currentTarget.value)}
        />
        <Button type="submit" leftSection={<IconSearch size={16} />}>
          Suchen
        </Button>
        <Button variant="subtle" color="gray" leftSection={<IconX size={16} />} onClick={handleClear}>
          Zuruecksetzen
        </Button>
      </Group>
    </Paper>
  );
}
