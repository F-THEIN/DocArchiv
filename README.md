# DocArchiv

DocArchiv ist eine leichtgewichtige Dokumenten-Archiv-SPA als Docker-Service. Die Anwendung verwaltet einen durchsuchbaren Index fuer gescannte Dokumente; die PDFs selbst bleiben in Nextcloud und werden ueber generierte Links geoeffnet.

## Funktionsumfang

- Dokumente per REST API anlegen, anzeigen, aktualisieren und loeschen.
- Suche ueber Titel, Zusammenfassung und Dateiname mit PostgreSQL-Volltextsuche.
- Filter nach Tags, Dokumenttyp und Datum.
- React-SPA mit Mantine-Oberflaeche.
- Automatische Datenbankmigration beim Containerstart.
- Docker-Compose-Setup fuer App und PostgreSQL.

## Architektur

```text
DocArchiv
├── backend/              # FastAPI, Domain, Infrastruktur, Alembic, Tests
├── frontend/             # Vite, React, TypeScript, Mantine
├── plans/                # Umsetzungsplan und Spezifikation
├── Dockerfile            # Multi-Stage-Build fuer Frontend und Backend
├── docker-compose.yml    # App + PostgreSQL fuer Deployment
└── .env.example          # Beispielkonfiguration
```

Backend-Schichtung:

- `backend/domain/`: Domain-Models, Schemas und Services.
- `backend/api/`: FastAPI-Router und Dependencies.
- `backend/infrastructure/`: Datenbank-Session und Repositories.

## Ports

| Zweck | Port |
| --- | --- |
| Container-App | `8000` |
| Docker-Compose Host-Port | `8088` |
| Lokaler Vite-Dev-Server | `5173` |

Nach einem Compose-Deployment ist DocArchiv unter `http://<server-ip>:8088` erreichbar.

## Konfiguration

Die wichtigsten Umgebungsvariablen:

| Variable | Beschreibung | Beispiel |
| --- | --- | --- |
| `POSTGRES_DB` | Name der PostgreSQL-Datenbank | `docarchiv` |
| `POSTGRES_USER` | PostgreSQL-Benutzer | `docarchiv` |
| `POSTGRES_PASSWORD` | PostgreSQL-Passwort | `changeme` |
| `DATABASE_URL` | SQLAlchemy-Verbindungs-URL | `postgresql://docarchiv:changeme@docarchiv-db:5432/docarchiv` |
| `DOCARCHIV_NC_BASE_URL` | Nextcloud-Basis-URL fuer Dokumentlinks | `https://nextcloud.example.com/apps/files/?dir=/Documents/Scans` |
| `DOCARCHIV_LOG_LEVEL` | Logging-Level | `INFO` |

Vor Produktivbetrieb muss insbesondere `POSTGRES_PASSWORD` angepasst werden.

## Deployment mit Portainer auf Ubuntu

Diese Anleitung geht davon aus, dass auf dem Ubuntu-Server Docker und Portainer bereits laufen.

### 1. Repository auf den Server bringen

Empfohlen ist ein Git-basiertes Deployment in Portainer:

1. Repository in ein Git-Remote pushen, zum Beispiel GitHub, Gitea oder GitLab.
2. Sicherstellen, dass folgende Dateien im Repository vorhanden sind:
   - `Dockerfile`
   - `docker-compose.yml`
   - `.env.example`
   - `backend/entrypoint.sh`
   - `backend/alembic/versions/001_initial_schema.py`
   - `frontend/package-lock.json`

Alternativ kann der Inhalt von `docker-compose.yml` direkt im Portainer-Web-Editor eingefuegt werden. Fuer den Build muss Portainer dann Zugriff auf das komplette Repository beziehungsweise Build-Kontext haben.

### 2. Portainer-Stack anlegen

In Portainer:

1. `Stacks` oeffnen.
2. `Add stack` waehlen.
3. Stack-Name setzen, zum Beispiel `docarchiv`.
4. Als Build-Quelle bevorzugt `Repository` waehlen.
5. Git-Repository-URL eintragen.
6. Compose-Pfad auf `docker-compose.yml` setzen.
7. Branch setzen, zum Beispiel `main`.

### 3. Environment Variables in Portainer setzen

Im Stack unter `Environment variables` mindestens diese Werte setzen:

```env
POSTGRES_DB=docarchiv
POSTGRES_USER=docarchiv
POSTGRES_PASSWORD=ein-sehr-sicheres-passwort
DOCARCHIV_NC_BASE_URL=https://nextcloud.example.com/apps/files/?dir=/Documents/Scans
DOCARCHIV_LOG_LEVEL=INFO
```

`DATABASE_URL` muss bei Nutzung von `docker-compose.yml` nicht zwingend gesetzt werden, weil sie aus den PostgreSQL-Werten zusammengesetzt wird. Wenn sie gesetzt wird, muss sie auf den Compose-Service `docarchiv-db` zeigen:

```env
DATABASE_URL=postgresql://docarchiv:ein-sehr-sicheres-passwort@docarchiv-db:5432/docarchiv
```

### 4. Stack deployen

1. In Portainer `Deploy the stack` ausfuehren.
2. Portainer baut das Image ueber den Multi-Stage-`Dockerfile`:
   - Node-Stage baut die React-SPA.
   - Python-Stage installiert Backend-Abhaengigkeiten.
   - Die gebaute SPA wird nach `backend/static` kopiert.
3. Beim Start fuehrt `backend/entrypoint.sh` automatisch `alembic upgrade head` aus.
4. Danach startet Uvicorn auf Port `8000` im Container.

### 5. Erreichbarkeit pruefen

Im Browser:

```text
http://<ubuntu-server-ip>:8088
```

Health-Endpunkt:

```text
http://<ubuntu-server-ip>:8088/api/health
```

Erwartete Health-Antwort:

```json
{
  "status": "ok",
  "service": "DocArchiv",
  "version": "0.1.0"
}
```

### 6. Firewall auf Ubuntu pruefen

Falls die Anwendung nicht erreichbar ist, Port `8088` freigeben:

```bash
sudo ufw allow 8088/tcp
sudo ufw status
```

Wenn Portainer selbst noch nicht erreichbar ist, sind je nach Installation typischerweise auch Port `9443` oder `9000` relevant.

### 7. Updates ueber Portainer

Bei Aenderungen:

1. Aenderungen ins Git-Repository pushen.
2. In Portainer den Stack oeffnen.
3. `Pull and redeploy` beziehungsweise `Update the stack` ausfuehren.
4. Logs der Services `docarchiv-app` und `docarchiv-db` pruefen.

## Lokale Entwicklung

### Backend vorbereiten

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
```

Backend-Code kompilieren:

```bash
PYTHONPATH=backend .venv/bin/python -m compileall backend
```

Tests ausfuehren:

```bash
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests
```

Backend lokal starten, wenn eine PostgreSQL-Datenbank verfuegbar ist:

```bash
PYTHONPATH=backend .venv/bin/python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend vorbereiten

```bash
cd frontend
npm install
npm run build
```

Frontend-Dev-Server:

```bash
cd frontend
npm run dev
```

Der Vite-Dev-Server leitet `/api` an `http://localhost:8000` weiter.

## Docker Compose lokal

Wenn Docker lokal verfuegbar ist:

```bash
cp .env.example .env
# .env anpassen

docker compose up --build -d
```

Logs anzeigen:

```bash
docker compose logs -f docarchiv-app
```

Stack stoppen:

```bash
docker compose down
```

Datenbank-Volume behalten:

```bash
docker compose down
```

Datenbank-Volume loeschen:

```bash
docker compose down -v
```

## Datenbankmigrationen

Migrationen liegen unter `backend/alembic/versions/`. Beim Containerstart wird automatisch ausgefuehrt:

```bash
alembic upgrade head
```

Manuell lokal ausfuehren:

```bash
cd backend
DATABASE_URL=postgresql://docarchiv:changeme@localhost:5432/docarchiv ../.venv/bin/alembic upgrade head
```

## Backup-Hinweis fuer Portainer/Ubuntu

Die PostgreSQL-Daten liegen im Docker-Volume `docarchiv-db-data`. Fuer produktive Nutzung sollte dieses Volume regelmaessig gesichert werden.

Beispiel fuer ein logisches Backup auf dem Ubuntu-Host:

```bash
docker exec docarchiv-db pg_dump -U docarchiv docarchiv > docarchiv-backup.sql
```

Restore-Beispiel:

```bash
cat docarchiv-backup.sql | docker exec -i docarchiv-db psql -U docarchiv docarchiv
```

## API-Uebersicht

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/health` | Health-Check |
| `GET` | `/api/documents` | Dokumentliste mit Suche und Filtern |
| `GET` | `/api/documents/{id}` | Dokumentdetails |
| `POST` | `/api/documents` | Dokument anlegen |
| `PUT` | `/api/documents/{id}` | Dokument aktualisieren |
| `DELETE` | `/api/documents/{id}` | Dokument loeschen |
| `GET` | `/api/documents/types` | Dokumenttypen |
| `GET` | `/api/tags` | Tags auflisten |
| `POST` | `/api/tags` | Tag anlegen |
| `GET` | `/api/tags/{id}` | Tagdetails |
| `DELETE` | `/api/tags/{id}` | Tag loeschen |

## Validierung vor Commits

Empfohlene Checks:

```bash
PYTHONPATH=backend .venv/bin/python -m compileall backend
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests
cd frontend && npm run build
```

Wenn Docker verfuegbar ist:

```bash
docker compose config --quiet
docker compose build
```
