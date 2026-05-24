import { Alert, Button, Card, Group, Modal, Stack, Text, TextInput, ThemeIcon, Title } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconAlertTriangle, IconDatabaseX } from '@tabler/icons-react';
import { useState } from 'react';

import type { ResetDatabaseResponse } from '../../types/document';

const CONFIRMATION_TEXT = 'LÖSCHEN';

interface ResetDatabaseCardProps {
  isResetting: boolean;
  onReset: () => Promise<ResetDatabaseResponse>;
  onAfterReset: () => Promise<void>;
}

export function ResetDatabaseCard({ isResetting, onReset, onAfterReset }: ResetDatabaseCardProps): React.ReactElement {
  const [opened, setOpened] = useState<boolean>(false);
  const [confirmation, setConfirmation] = useState<string>('');

  const isConfirmed = confirmation === CONFIRMATION_TEXT;

  function closeModal(): void {
    if (isResetting) {
      return;
    }
    setOpened(false);
    setConfirmation('');
  }

  async function handleReset(): Promise<void> {
    if (!isConfirmed) {
      return;
    }

    try {
      const response = await onReset();
      await onAfterReset();
      notifications.show({
        title: 'Datenbank zurückgesetzt',
        message: `${response.deleted_documents} Dokumente und ${response.deleted_tags} Tags wurden gelöscht.`,
        color: 'green',
      });
      closeModal();
    } catch (error: unknown) {
      notifications.show({
        title: 'Zurücksetzen fehlgeschlagen',
        message: error instanceof Error ? error.message : 'Die Datenbank konnte nicht zurückgesetzt werden.',
        color: 'red',
      });
    }
  }

  return (
    <>
      <Card
        withBorder
        radius={16}
        p="lg"
        style={{
          background: 'linear-gradient(145deg, rgba(231, 76, 60, 0.16), var(--navy-card))',
          border: '1.5px solid rgba(231, 76, 60, 0.45)',
          boxShadow: '0 12px 20px rgba(0, 0, 0, 0.35)',
        }}
      >
        <Stack gap="md">
          <Group justify="space-between" align="flex-start">
            <Group gap="sm" align="flex-start" wrap="nowrap">
              <ThemeIcon size={44} radius={12} variant="filled" style={{ background: 'rgba(231, 76, 60, 0.22)', color: 'var(--red)' }}>
                <IconDatabaseX size={24} />
              </ThemeIcon>
              <Stack gap={4}>
                <Text c="var(--red)" fw={800} size="10px" tt="uppercase" style={{ letterSpacing: '0.12em', fontFamily: '"Montserrat", sans-serif' }}>
                  Gefahrenzone
                </Text>
                <Title order={2} size="h3" c="white" style={{ fontFamily: '"Montserrat", sans-serif' }}>
                  Datenbank zurücksetzen
                </Title>
                <Text c="var(--white-70)" size="sm">
                  Löscht alle Dokumente, Tags und Zuordnungen. Die PDF-Dateien in Nextcloud bleiben unverändert.
                </Text>
              </Stack>
            </Group>
          </Group>

          <Alert
            icon={<IconAlertTriangle size={18} />}
            color="red"
            title="Unwiderrufliche Aktion"
            styles={{
              root: { background: 'rgba(231, 76, 60, 0.12)', border: '1px solid rgba(231, 76, 60, 0.35)' },
              title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
              message: { color: 'var(--white-70)' },
            }}
          >
            Diese Aktion eignet sich nur für Tests oder einen kompletten Neustart des Archivs.
          </Alert>

          <Group justify="flex-end">
            <Button color="red" leftSection={<IconDatabaseX size={18} />} onClick={() => setOpened(true)} loading={isResetting}>
              Datenbank zurücksetzen
            </Button>
          </Group>
        </Stack>
      </Card>

      <Modal
        opened={opened}
        onClose={closeModal}
        title="Datenbank wirklich zurücksetzen?"
        centered
        styles={{
          content: { background: 'var(--navy-card)', border: '1px solid rgba(231, 76, 60, 0.45)' },
          header: { background: 'var(--navy-card)' },
          title: { color: 'white', fontFamily: '"Montserrat", sans-serif', fontWeight: 800 },
        }}
      >
        <Stack gap="md">
          <Text c="var(--white-70)" size="sm">
            Diese Aktion löscht <strong>alle Dokumente und Tags</strong> in der Datenbank. Zum Bestätigen bitte exakt{' '}
            <Text span c="var(--red)" fw={900}>
              {CONFIRMATION_TEXT}
            </Text>{' '}
            eingeben.
          </Text>

          <TextInput
            label="Bestätigung"
            placeholder={CONFIRMATION_TEXT}
            value={confirmation}
            onChange={(event) => setConfirmation(event.currentTarget.value)}
            disabled={isResetting}
            styles={{
              label: { color: 'white', fontWeight: 700 },
              input: { background: 'var(--white-15)', borderColor: 'var(--white-15)', color: 'white' },
            }}
          />

          <Group justify="flex-end">
            <Button variant="subtle" color="gray" onClick={closeModal} disabled={isResetting}>
              Abbrechen
            </Button>
            <Button color="red" onClick={() => void handleReset()} disabled={!isConfirmed} loading={isResetting}>
              Endgültig löschen
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
}
