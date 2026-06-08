import { Alert, Anchor, Badge, Button, Drawer, Group, List, MultiSelect, Select, Stack, Text, Textarea, TextInput, Title } from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { IconAlertCircle, IconExternalLink, IconPencil, IconUser } from '@tabler/icons-react';
import { useState } from 'react';

import type { Correspondent, DocumentSummary, DocumentTypeInfo, Tag, UpdateDocumentPayload } from '../../types/document';

interface DocumentDetailProps {
  document: DocumentSummary | null;
  opened: boolean;
  correspondents: Correspondent[];
  documentTypes: DocumentTypeInfo[];
  tags: Tag[];
  onClose: () => void;
  onUpdate: (id: number, payload: UpdateDocumentPayload) => Promise<DocumentSummary>;
}

const INPUT_STYLES = {
  label: { color: 'var(--white-40)', fontFamily: '"Montserrat", sans-serif', textTransform: 'uppercase' as const, letterSpacing: '0.07em' },
  input: { background: 'var(--navy-card)', borderColor: 'var(--white-15)', color: 'white' },
};

const DROPDOWN_STYLES = {
  ...INPUT_STYLES,
  dropdown: { background: 'var(--navy-card)', borderColor: 'var(--white-15)' },
  option: { color: 'white' },
};

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

function formatOptionalDate(value: string | null): string {
  if (value === null) {
    return 'Nicht gesetzt';
  }

  return new Intl.DateTimeFormat('de-DE').format(new Date(value));
}

function parseDateValue(value: string | null): Date | null {
  if (value === null) {
    return null;
  }

  const parsed = new Date(value);
  return isNaN(parsed.getTime()) ? null : parsed;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return 'Dokument konnte nicht gespeichert werden.';
}

export function DocumentDetail({
  document,
  opened,
  correspondents,
  documentTypes,
  tags,
  onClose,
  onUpdate,
}: DocumentDetailProps): React.ReactElement {
  const [editMode, setEditMode] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [correspondentId, setCorrespondentId] = useState<string | null>(null);
  const [documentTypeId, setDocumentTypeId] = useState<string | null>(null);
  const [documentDate, setDocumentDate] = useState<Date | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  function enterEditMode(): void {
    if (document === null) return;
    setTitle(document.title);
    setSummary(document.summary ?? '');
    setCorrespondentId(document.correspondent_id !== null ? String(document.correspondent_id) : null);
    setDocumentTypeId(String(document.document_type_id));
    setDocumentDate(parseDateValue(document.document_date));
    setSelectedTags(document.tags.map((t) => t.name));
    setSaveError(null);
    setEditMode(true);
  }

  function handleClose(): void {
    setEditMode(false);
    setSaveError(null);
    onClose();
  }

  async function handleSave(): Promise<void> {
    if (document === null || documentTypeId === null) return;

    const trimmedTitle = title.trim();

    if (trimmedTitle.length === 0) {
      setSaveError('Titel darf nicht leer sein.');
      return;
    }

    setIsSaving(true);
    setSaveError(null);

    try {
      const payload: UpdateDocumentPayload = {
        title: trimmedTitle,
        summary: summary.trim(),
        correspondent_id: correspondentId !== null ? Number(correspondentId) : null,
        document_type_id: Number(documentTypeId),
        document_date: documentDate !== null ? documentDate.toISOString().slice(0, 10) : null,
        tags: selectedTags,
      };
      await onUpdate(document.id, payload);
      setEditMode(false);
    } catch (error: unknown) {
      setSaveError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  }

  const correspondentOptions = correspondents.map((c) => ({ value: String(c.id), label: c.name }));
  const documentTypeOptions = documentTypes.map((dt) => ({ value: String(dt.id), label: dt.name }));
  const tagOptions = tags.map((t) => ({ value: t.name, label: t.name }));

  const drawerKey = document !== null ? `${document.id}-${editMode ? 'edit' : 'view'}` : 'empty';

  return (
    <Drawer
      key={drawerKey}
      opened={opened}
      onClose={handleClose}
      position="right"
      size="lg"
      title={editMode ? 'Dokument bearbeiten' : 'Dokumentdetails'}
      styles={{
        content: { background: 'var(--navy-mid)', color: 'white' },
        header: {
          background: editMode ? 'var(--navy-card)' : 'var(--navy-mid)',
          borderBottom: '1px solid var(--white-15)',
        },
        title: { color: editMode ? 'var(--gold)' : 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
        close: { color: 'var(--white-70)' },
      }}
    >
      {document === null ? null : editMode ? (
        <Stack gap="lg">
          <TextInput
            label="Titel"
            required
            value={title}
            onChange={(e) => setTitle(e.currentTarget.value)}
            styles={INPUT_STYLES}
          />

          <Textarea
            label="Zusammenfassung"
            value={summary}
            onChange={(e) => setSummary(e.currentTarget.value)}
            autosize
            minRows={3}
            styles={INPUT_STYLES}
          />

          <Select
            label="Dokumenttyp"
            required
            data={documentTypeOptions}
            value={documentTypeId}
            onChange={setDocumentTypeId}
            styles={DROPDOWN_STYLES}
          />

          <Select
            label="Korrespondent"
            data={correspondentOptions}
            value={correspondentId}
            onChange={setCorrespondentId}
            clearable
            clearButtonProps={{ style: { color: 'var(--white-70)' } }}
            styles={DROPDOWN_STYLES}
          />

          <DateInput
            label="Dokumentdatum"
            value={documentDate}
            onChange={setDocumentDate}
            clearable
            valueFormat="DD.MM.YYYY"
            locale="de"
            styles={DROPDOWN_STYLES}
          />

          <MultiSelect
            label="Tags"
            data={tagOptions}
            value={selectedTags}
            onChange={setSelectedTags}
            styles={DROPDOWN_STYLES}
          />

          {saveError !== null ? (
            <Alert
              icon={<IconAlertCircle size={18} />}
              title="Fehler beim Speichern"
              styles={{
                root: { background: 'var(--navy-card)', border: '1px solid var(--mantine-color-red-8)' },
                title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
                message: { color: 'var(--white-70)' },
              }}
            >
              {saveError}
            </Alert>
          ) : null}

          <Group justify="flex-end">
            <Button
              variant="transparent"
              onClick={() => setEditMode(false)}
              disabled={isSaving}
              styles={{ root: { border: '1px solid var(--white-15)', color: 'var(--white-40)' } }}
            >
              Abbrechen
            </Button>
            <Button
              loading={isSaving}
              onClick={() => void handleSave()}
              styles={{ root: { background: 'var(--gold)', color: 'var(--navy)', fontFamily: '"Montserrat", sans-serif', fontWeight: 700 } }}
            >
              Speichern
            </Button>
          </Group>
        </Stack>
      ) : (
        <Stack gap="lg">
          <Stack gap="xs">
            <Group justify="space-between" align="flex-start" wrap="nowrap">
              <Title order={2} c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                {document.title}
              </Title>
              <Button
                leftSection={<IconPencil size={14} />}
                size="xs"
                onClick={enterEditMode}
                styles={{ root: { background: 'var(--white-15)', color: 'var(--white-70)', flexShrink: 0 } }}
              >
                Bearbeiten
              </Button>
            </Group>
            <Text c="var(--white-40)">{document.original_filename}</Text>
            <Group gap="xs">
              <Badge styles={{ root: { background: 'var(--white-15)', color: 'var(--white-70)' } }}>{document.document_type.name}</Badge>
              <Badge styles={{ root: { borderColor: 'var(--white-15)', color: 'var(--white-40)' } }} variant="outline">
                {formatOptionalDate(document.document_date)}
              </Badge>
            </Group>
          </Stack>

          {document.correspondent !== null ? (
            <Stack gap="xs">
              <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                Korrespondent
              </Title>
              <Group gap="xs">
                <IconUser size={16} color="var(--blue)" />
                <Text c="var(--white-70)">{document.correspondent.name}</Text>
              </Group>
            </Stack>
          ) : null}

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Zusammenfassung
            </Title>
            <Text c="var(--white-70)">{document.summary || 'Keine Zusammenfassung vorhanden.'}</Text>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Tags
            </Title>
            <Group gap="xs">
              {document.tags.length > 0 ? (
                document.tags.map((tag) => (
                  <Badge key={tag.id} styles={{ root: { background: 'var(--white-15)', color: 'var(--white-70)' } }}>
                    {tag.name}
                  </Badge>
                ))
              ) : (
                <Text c="var(--white-40)">Keine Tags vergeben.</Text>
              )}
            </Group>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Ablage
            </Title>
            <List spacing="xs">
              <List.Item>
                <Text span fw={600} c="var(--white-70)">
                  Gespeicherter Dateiname:{' '}
                </Text>
                <Text span c="var(--white-40)">
                  {document.stored_filename}
                </Text>
              </List.Item>
              <List.Item>
                <Text span fw={600} c="var(--white-70)">
                  Nextcloud-Pfad:{' '}
                </Text>
                <Text span c="var(--white-40)">
                  {document.nextcloud_path}
                </Text>
              </List.Item>
              <List.Item>
                <Anchor href={document.nextcloud_url} target="_blank" rel="noreferrer" c="var(--gold)">
                  <Group gap={6} component="span">
                    In Nextcloud oeffnen
                    <IconExternalLink size={16} />
                  </Group>
                </Anchor>
              </List.Item>
            </List>
          </Stack>

          <Stack gap="xs">
            <Title order={3} size="h4" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
              Metadaten
            </Title>
            <Text size="sm" c="var(--white-40)">
              Erstellt: {formatDateTime(document.created_at)}
            </Text>
            <Text size="sm" c="var(--white-40)">
              Aktualisiert: {formatDateTime(document.updated_at)}
            </Text>
          </Stack>
        </Stack>
      )}
    </Drawer>
  );
}
