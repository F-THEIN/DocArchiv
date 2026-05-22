import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';

import { App } from './App';
import { theme } from './theme';

const rootElement = document.getElementById('root');

if (rootElement === null) {
  throw new Error('Root-Element wurde nicht gefunden.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <MantineProvider theme={theme} defaultColorScheme="light">
      <Notifications position="top-right" />
      <App />
    </MantineProvider>
  </React.StrictMode>,
);
