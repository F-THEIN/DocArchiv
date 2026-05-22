import { Anchor, Badge, Group, ScrollArea, Stack, Text } from '@mantine/core';

import type { Tag } from '../../types/document';

interface TagCloudProps {
  tags: Tag[];
  selectedTags: string[];
  onToggleTag: (tagName: string) => void;
  onEditTag?: (tag: Tag) => void;
}

export function TagCloud({ tags, selectedTags, onToggleTag, onEditTag }: TagCloudProps): React.ReactElement {
  if (tags.length === 0) {
    return (
      <Stack gap={4} px="xs">
        <Group justify="space-between">
          <Text c="var(--gold)" fw={800} size="13px" tt="uppercase" style={{ letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif' }}>
            ✦ Tag-Schnellauswahl
          </Text>
          <Text size="11px" c="var(--white-40)">
            Keine Tags
          </Text>
        </Group>
        <Text size="sm" c="var(--white-40)">
          Noch keine Tags vorhanden.
        </Text>
      </Stack>
    );
  }

  return (
    <Stack gap="sm" px="xs">
      <Group justify="space-between" align="center">
        <Text c="var(--gold)" fw={800} size="13px" tt="uppercase" style={{ letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif' }}>
          ✦ Tag-Schnellauswahl
        </Text>
        <Group gap="sm">
          <Text size="11px" c="var(--white-40)">
            {tags.length} verfuegbar
          </Text>
          {onEditTag !== undefined ? (
            <Anchor
              component="button"
              type="button"
              size="11px"
              c="var(--white-40)"
              style={{ textDecorationColor: 'var(--white-15)' }}
              onClick={() => onEditTag(tags[0])}
            >
              Tags verwalten
            </Anchor>
          ) : null}
        </Group>
      </Group>

      <ScrollArea
        type="never"
        scrollbarSize={0}
        style={{ width: '100%' }}
        styles={{ viewport: { paddingBottom: 2, scrollbarWidth: 'none', WebkitOverflowScrolling: 'touch' } }}
      >
        <Group gap="xs" wrap="nowrap">
          {tags.map((tag, index) => {
            const isSelected = selectedTags.includes(tag.name);
            const activeColor = index % 3 === 0 ? 'var(--gold)' : index % 3 === 1 ? '#2563be' : 'var(--teal)';

            return (
              <Badge
                key={tag.id}
                component="button"
                type="button"
                radius="xl"
                onClick={() => onToggleTag(tag.name)}
                styles={{
                  root: {
                    cursor: 'pointer',
                    borderRadius: 100,
                    fontFamily: '"Montserrat", sans-serif',
                    fontWeight: 700,
                    fontSize: 11,
                    textTransform: 'uppercase',
                    letterSpacing: '0.07em',
                    border: '1px solid var(--white-15)',
                    background: isSelected ? activeColor : 'var(--navy-card)',
                    color: isSelected ? '#0f1f3d' : 'var(--white-40)',
                    paddingRight: 10,
                    paddingLeft: 10,
                  },
                }}
              >
                {tag.name}
                <Text span c={isSelected ? 'rgba(15,31,61,0.65)' : 'rgba(255,255,255,0.65)'}>
                  {' '}
                  ·{tag.document_count}
                </Text>
              </Badge>
            );
          })}
        </Group>
      </ScrollArea>
    </Stack>
  );
}
