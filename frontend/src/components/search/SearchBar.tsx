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
    <Paper
      component="form"
      withBorder
      radius="xl"
      p="md"
      shadow="sm"
      onSubmit={handleSubmit}
      style={{
        borderColor: 'rgba(255, 122, 24, 0.25)',
        background: 'linear-gradient(160deg, rgba(255, 255, 255, 0.96) 0%, rgba(255, 245, 232, 0.92) 100%)',
      }}
    >
      <Group align="flex-end" gap="sm">
        <TextInput
          flex={1}
          label="Volltextsuche"
          placeholder="Titel, Zusammenfassung oder Dateiname suchen"
          leftSection={<IconSearch size={18} />}
          value={draftValue}
          onChange={(event) => setDraftValue(event.currentTarget.value)}
        />
        <Button type="submit" variant="gradient" gradient={{ from: 'orange.5', to: 'pink.5', deg: 120 }} leftSection={<IconSearch size={16} />}>
          Suchen
        </Button>
        <Button variant="light" color="gray" leftSection={<IconX size={16} />} onClick={handleClear}>
          Zuruecksetzen
        </Button>
      </Group>
    </Paper>
  );
}
