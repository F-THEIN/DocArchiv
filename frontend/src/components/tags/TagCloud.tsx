import { Badge, Group, Paper, Stack, Text, Title } from '@mantine/core';

import type { Tag } from '../../types/document';

interface TagCloudProps {
  tags: Tag[];
  selectedTags: string[];
  onToggleTag: (tagName: string) => void;
}

export function TagCloud({ tags, selectedTags, onToggleTag }: TagCloudProps): React.ReactElement {
  if (tags.length === 0) {
    return (
      <Paper withBorder radius="lg" p="md">
        <Stack gap={4}>
          <Title order={2} size="h4">
            Tags
          </Title>
          <Text size="sm" c="dimmed">
            Noch keine Tags vorhanden.
          </Text>
        </Stack>
      </Paper>
    );
  }

  return (
    <Paper withBorder radius="lg" p="md">
      <Stack gap="sm">
        <Stack gap={2}>
          <Title order={2} size="h4">
            Tag-Schnellauswahl
          </Title>
          <Text size="sm" c="dimmed">
            Klick auf einen Tag aktiviert oder entfernt den Filter.
          </Text>
        </Stack>

        <Group gap="xs">
          {tags.map((tag) => {
            const isSelected = selectedTags.includes(tag.name);

            return (
              <Badge
                key={tag.id}
                component="button"
                type="button"
                color={tag.color ?? 'blue'}
                variant={isSelected ? 'filled' : 'light'}
                size="lg"
                radius="xl"
                styles={{ root: { cursor: 'pointer' } }}
                onClick={() => onToggleTag(tag.name)}
              >
                {tag.name} · {tag.document_count}
              </Badge>
            );
          })}
        </Group>
      </Stack>
    </Paper>
  );
}
