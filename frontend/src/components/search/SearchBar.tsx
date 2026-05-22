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
      radius={16}
      p="md"
      onSubmit={handleSubmit}
      style={{
        borderColor: 'var(--white-15)',
        background: 'var(--navy-mid)',
        boxShadow: '0 10px 20px rgba(0, 0, 0, 0.35)',
      }}
    >
      <Group align="flex-end" gap="sm" wrap="wrap">
        <TextInput
          flex={1}
          label="Volltextsuche"
          placeholder="Titel, Zusammenfassung oder Dateiname suchen"
          leftSection={<IconSearch size={18} />}
          value={draftValue}
          onChange={(event) => setDraftValue(event.currentTarget.value)}
          styles={{
            label: {
              color: 'var(--white-40)',
              fontFamily: '"Montserrat", sans-serif',
              textTransform: 'uppercase',
              letterSpacing: '0.07em',
              fontSize: '10px',
            },
            input: {
              background: 'var(--navy-card)',
              border: '1.5px solid var(--white-15)',
              color: 'white',
              fontFamily: '"Open Sans", sans-serif',
              '&::placeholder': { color: 'var(--white-40)' },
              '&:focus': { borderColor: 'var(--gold)' },
            },
            section: { color: 'var(--white-40)' },
          }}
        />
        <Button
          type="submit"
          leftSection={<IconSearch size={16} />}
          styles={{
            root: {
              background: 'var(--gold)',
              color: 'var(--navy)',
              fontFamily: '"Montserrat", sans-serif',
              fontWeight: 700,
              border: '1px solid transparent',
            },
          }}
        >
          Suchen
        </Button>
        <Button
          variant="transparent"
          leftSection={<IconX size={16} />}
          onClick={handleClear}
          styles={{
            root: {
              color: 'var(--white-40)',
              border: '1px solid var(--white-15)',
              fontFamily: '"Montserrat", sans-serif',
              fontWeight: 700,
            },
          }}
        >
          Zuruecksetzen
        </Button>
      </Group>
    </Paper>
  );
}
