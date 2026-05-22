import React from 'react';
import ReactDOM from 'react-dom/client';
import '@mantine/core/styles.css';

function App(): React.ReactElement {
  return (
    <main>
      <h1>DocArchiv</h1>
      <p>Frontend-Grundgeruest ist bereit.</p>
    </main>
  );
}

const rootElement = document.getElementById('root');

if (rootElement === null) {
  throw new Error('Root-Element wurde nicht gefunden.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
