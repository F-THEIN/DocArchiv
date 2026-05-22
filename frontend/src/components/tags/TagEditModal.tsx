import { Button, ColorInput, Group, Modal, TextInput } from '@mantine/core';
import { useState } from 'react';

import { apiClient, ApiError } from '../../api/client';
import type { Tag } from '../../types/document';

interface TagEditModalProps {
  tag: Tag | null;
  opened: boolean;
  onClose: () => void;
  onSaved: () => void;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Tag konnte nicht gespeichert werden.';
}

export function TagEditModal({ tag, opened, onClose, onSaved }: TagEditModalProps): React.ReactElement {
  const [name, setName] = useState(tag?.name ?? '');
  const [color, setColor] = useState(tag?.color ?? '');
  const [nameError, setNameError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  function handleClose(): void {
    setName(tag?.name ?? '');
    setColor(tag?.color ?? '');
    setNameError(null);
    setSaveError(null);
    onClose();
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();

    if (tag === null) {
      return;
    }

    const trimmedName = name.trim();

    if (trimmedName.length === 0) {
      setNameError('Name darf nicht leer sein.');
      return;
    }

    setNameError(null);
    setIsSaving(true);
    setSaveError(null);

    try {
      await apiClient.updateTag(tag.id, {
        name: trimmedName,
        color: color.trim() || null,
      });
      onSaved();
    } catch (error: unknown) {
      setSaveError(getErrorMessage(error));
    } finally {
      setIsSaving(false);
    }
  }

  // Formular mit aktuellem Tag befuellen, wenn sich der Tag aendert
  const modalKey = tag ? `${tag.id}-${tag.name}-${tag.color ?? ''}` : 'empty';

  return (
    <Modal key={modalKey} opened={opened} onClose={handleClose} title="Tag bearbeiten" size="sm">
      <form onSubmit={(e) => void handleSubmit(e)}>
        <TextInput
          label="Name"
          placeholder="Tag-Name"
          required
          mb="sm"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          error={nameError}
        />
        <ColorInput
          label="Farbe"
          placeholder="#003B7E"
          mb="md"
          value={color}
          onChange={setColor}
        />
        {saveError !== null ? (
          <p style={{ color: 'var(--mantine-color-red-6)', fontSize: '0.875rem', marginBottom: '0.75rem' }}>
            {saveError}
          </p>
        ) : null}
        <Group justify="flex-end">
          <Button variant="default" onClick={handleClose} disabled={isSaving}>
            Abbrechen
          </Button>
          <Button type="submit" loading={isSaving}>
            Speichern
          </Button>
        </Group>
      </form>
    </Modal>
  );
}
