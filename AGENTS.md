# AGENTS.md – DocArchiv-Konventionen

Diese Datei definiert verbindliche Regeln fuer Agents und Entwickler in diesem Repository.

## Projektziel

DocArchiv ist eine leichtgewichtige Dokumenten-Archiv-SPA als Docker-Service. Die Anwendung ist ein Index fuer gescannte Dokumente; die PDFs bleiben in Nextcloud.

## Sprache und Stil

- Dokumentation, Kommentare und Docstrings werden auf Deutsch geschrieben.
- Code, Variablennamen, Funktionsnamen, Klassen und API-Felder werden auf Englisch geschrieben.
- Keine echten Secrets committen. Nur Platzhalter in `.env.example` verwenden.
- Commit-Messages folgen dem Schema `<typ>: <beschreibung>`, zum Beispiel `feat: add document schemas`.

## Backend-Konventionen

- Python-Version: 3.12.
- Framework: FastAPI.
- ORM: SQLAlchemy 2.0.
- Migrations: Alembic.
- Pydantic: Version 2 fuer alle Request- und Response-Schemas.
- Type Hints sind verpflichtend.
- Module und oeffentliche Funktionen/Klassen erhalten Docstrings.
- Logging erfolgt ueber das Python-Logging-Modul.

## DDD-Schichtung

Das Backend folgt einer schlanken DDD-Struktur:

- `backend/domain/`: Domain-Models, Schemas und Business-Logik.
- `backend/api/`: HTTP-Endpunkte und FastAPI-Dependencies.
- `backend/infrastructure/`: Datenbank, Sessions und Repositories.

Regeln:

- API-Endpunkte bleiben duenn: Request validieren, Service aufrufen, Response zurueckgeben.
- Business-Logik lebt in `backend/domain/services.py`.
- Datenbankabfragen leben in `backend/infrastructure/repositories.py`.
- Services greifen ueber Repositories auf Daten zu, nicht direkt ueber rohe Query-Logik.
- Domain-Code importiert nicht aus dem API-Layer.

## Tests und lokale Pruefung

Vor sinnvollen Commits sollen mindestens diese Checks laufen:

1. Virtuelle Umgebung verwenden oder erstellen.
2. Backend-Abhaengigkeiten aus `backend/requirements.txt` installieren.
3. Python-Code kompilieren lassen.
4. Sobald Tests vorhanden sind, pytest ausfuehren.

Beispielablauf ohne Secrets:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
PYTHONPATH=backend .venv/bin/python -m compileall backend
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests
```

## Git-Konventionen

- Hauefig kleine, thematisch klare Commits erstellen.
- Vor jedem Commit `git status --short` pruefen.
- Keine lokalen Artefakte committen, insbesondere `.venv/`, `__pycache__/`, `.env`, `node_modules/` und Build-Ordner.
- Nach jeder abgeschlossenen Phase einen Commit erstellen.

## Frontend-Konventionen

- TypeScript strict verwenden.
- Keine `any`-Types.
- Mantine-Komponenten bevorzugen.
- Datenlogik in Custom Hooks kapseln.
- Fetch-basierten API-Client verwenden, kein axios.
- Kein globaler State-Manager, solange React State und URL-Parameter ausreichen.

## Docker-Konventionen

- Multi-Stage-Build: Node fuer Frontend, Python fuer Runtime.
- FastAPI serviert die gebaute SPA aus `static/`.
- Health-Endpunkt `/api/health` muss immer funktionieren.
- App-Port im Container: 8000.
- Host-Port fuer Compose: 8088.
