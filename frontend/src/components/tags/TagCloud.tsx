import { Anchor, Badge, Box, Group, ScrollArea, Stack, Text } from '@mantine/core';
import { useEffect, useRef } from 'react';

import type { Tag } from '../../types/document';

interface TagCloudProps {
  tags: Tag[];
  selectedTags: string[];
  onToggleTag: (tagName: string) => void;
  onEditTag?: (tag: Tag) => void;
}

const MIN_CHIP_TOUCH_WIDTH = 44;
const MIN_CHIP_TOUCH_HEIGHT = 36;
const CHIP_MIN_WIDTH = `max(${MIN_CHIP_TOUCH_WIDTH}px, max-content)`;

export function TagCloud({ tags, selectedTags, onToggleTag, onEditTag }: TagCloudProps): React.ReactElement {
  const visibleTags = tags.filter((tag) => tag.document_count > 0);
  const editableTag = tags.find((tag) => selectedTags.includes(tag.name)) ?? null;
  const tagElementMap = useRef<Record<string, HTMLButtonElement | null>>({});

  useEffect(() => {
    const selectedTagSet = new Set(selectedTags);
    const firstSelectedTagName = visibleTags.find((tag) => selectedTagSet.has(tag.name))?.name;

    if (!firstSelectedTagName) {
      return;
    }

    tagElementMap.current[firstSelectedTagName]?.scrollIntoView({ behavior: 'smooth', inline: 'nearest', block: 'nearest' });
  }, [selectedTags, visibleTags]);

  if (visibleTags.length === 0) {
    return (
      <Stack gap={4} px="xs">
        <Group justify="space-between">
          <Text c="var(--gold)" fw={800} size="13px" tt="uppercase" style={{ letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif' }}>
            ✦ Tag-Schnellauswahl
          </Text>
          <Text size="11px" c="var(--white-40)">
            Keine Treffer
          </Text>
        </Group>
        <Text size="sm" c="var(--white-40)">
          Aktuell sind keine Tags mit Treffern verfuegbar.
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
            {visibleTags.length} verfuegbar
          </Text>
          {onEditTag !== undefined ? (
            <Anchor
              component="button"
              type="button"
              size="11px"
              c={editableTag === null ? 'rgba(255,255,255,0.25)' : 'var(--white-40)'}
              style={{ textDecorationColor: 'var(--white-15)' }}
              onClick={() => {
                if (editableTag !== null) {
                  onEditTag(editableTag);
                }
              }}
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
        styles={{
          viewport: {
            paddingBottom: 2,
            scrollbarWidth: 'none',
            WebkitOverflowScrolling: 'touch',
            overflowY: 'hidden',
          },
        }}
      >
        <Box
          style={{
            display: 'flex',
            flexWrap: 'nowrap',
            gap: 'var(--mantine-spacing-xs)',
            minWidth: 'max-content',
          }}
        >
          {visibleTags.map((tag, index) => {
            const isSelected = selectedTags.includes(tag.name);
            const activeColor = index % 3 === 0 ? 'var(--gold)' : index % 3 === 1 ? '#2563be' : 'var(--teal)';

            return (
              <Badge
                key={tag.id}
                component="button"
                type="button"
                radius="xl"
                ref={(element) => {
                  tagElementMap.current[tag.name] = element;
                }}
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
                    width: 'auto',
                    minWidth: CHIP_MIN_WIDTH,
                    maxWidth: 'none',
                    minHeight: MIN_CHIP_TOUCH_HEIGHT,
                    padding: '7px 13px',
                    whiteSpace: 'nowrap',
                    overflow: 'visible',
                    flexShrink: 0,
                    lineHeight: 1,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  },
                }}
              >
                {tag.name}
                <Text span c={isSelected ? 'rgba(15,31,61,0.65)' : 'rgba(255,255,255,0.65)'}>
                  {' '}
                  · {tag.document_count}
                </Text>
              </Badge>
            );
          })}
        </Box>
      </ScrollArea>
    </Stack>
  );
}
