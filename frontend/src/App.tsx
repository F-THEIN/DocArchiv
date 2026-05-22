import { Anchor, Badge, Button, Container, Group, Paper, Stack, Text, Title } from '@mantine/core';
import { IconExternalLink, IconSearch } from '@tabler/icons-react';

export function App(): React.ReactElement {
  return (
    <Container component="main" size="lg" py="xl">
      <Stack gap="xl">
        <Paper withBorder shadow="sm" p="xl" radius="lg">
          <Stack gap="md">
            <Group justify="space-between" align="flex-start" gap="md">
              <Stack gap={4}>
                <Badge variant="light" color="blue" w="fit-content">
                  DocArchiv
                </Badge>
                <Title order={1}>Dokumente schneller wiederfinden</Title>
              </Stack>
              <Button leftSection={<IconSearch size={18} />} variant="filled">
                Suche vorbereiten
              </Button>
            </Group>

            <Text c="dimmed" size="lg" maw={760}>
              Das Frontend-Grundgeruest ist bereit. Die naechsten Schritte fuegen API-Client,
              Dokumentliste, Filter und Detailansicht hinzu.
            </Text>

            <Group gap="xs">
              <Badge color="gray" variant="outline">
                React
              </Badge>
              <Badge color="gray" variant="outline">
                TypeScript strict
              </Badge>
              <Badge color="gray" variant="outline">
                Mantine
              </Badge>
              <Badge color="gray" variant="outline">
                Vite
              </Badge>
            </Group>
          </Stack>
        </Paper>

        <Paper withBorder p="lg" radius="lg">
          <Group justify="space-between" align="center">
            <Stack gap={2}>
              <Title order={2} size="h3">
                Backend-Anbindung
              </Title>
              <Text c="dimmed">
                Die Vite-Entwicklungsumgebung leitet API-Aufrufe unter /api an FastAPI weiter.
              </Text>
            </Stack>
            <Anchor href="/api/health" target="_blank" rel="noreferrer">
              <Group gap={6}>
                Health-Endpunkt
                <IconExternalLink size={16} />
              </Group>
            </Anchor>
          </Group>
        </Paper>
      </Stack>
    </Container>
  );
}
