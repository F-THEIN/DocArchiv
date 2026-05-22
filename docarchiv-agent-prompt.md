# DocArchiv – Agent-Prompt

> Kopiere diesen Prompt in einen neuen Agent, der in einem leeren `DocArchiv`-Repository arbeitet.
> Der Plan liegt als Referenz bei: `plans/dokument-archiv-spa.md`

---

## Prompt

Du baust **DocArchiv** – eine leichtgewichtige Dokumenten-Archiv SPA als Docker-Service.

### Was ist DocArchiv?

Ein durchsuchbarer Katalog für gescannte Dokumente. Die eigentlichen PDFs liegen in Nextcloud – DocArchiv ist nur der Index mit Volltextsuche, Tagging und Linkout. Eine bestehende Scan-KI-Pipeline (Ollama) analysiert Dokumente und legt sie per REST API in DocArchiv an.

### Tech-Stack

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic
- **Datenbank:** PostgreSQL 16 (Volltextsuche mit `tsvector`, deutsche Stemming-Analyse, GIN-Index)
- **Frontend:** Vite + React + TypeScript + Mantine v7
- **Design:** EnBW-inspiriert – Primärfarbe `#003B7E` (Dunkelblau), Akzent `#00A550` (Grün), Hintergrund `#F5F7FA`, Card-basiert mit `border-radius: 12px`, Inter/System-Font, Tabler Icons
- **Container:** Multi-Stage Dockerfile (Node Build → Python Runtime), docker-compose.yml mit PostgreSQL
- **Port:** 8088 (Host) → 8000 (Container)
- **Auth:** Keins (nur LAN-intern)

### Datenbankschema

**documents:** id, title, summary (text), original_filename, stored_filename, document_type, document_date, nextcloud_path, nextcloud_url, created_at, updated_at, search_vector (tsvector, generated)

**tags:** id, name (unique, lowercase), color (optional)

**document_tags:** document_id, tag_id (M:N)

Volltextsuche: `search_vector` als GENERATED ALWAYS STORED mit gewichteter `tsvector` (Titel A, Summary B, Dateiname C), Sprache `german`, GIN-Index.

### REST API

| Methode | Pfad | Zweck |
|---------|------|-------|
| GET | /api/documents | Liste mit Suche (?q=), Filter (?tags=, ?type=, ?date_from=, ?date_to=), Pagination (?page=, ?per_page=), Sortierung (?sort=) |
| GET | /api/documents/{id} | Einzelnes Dokument |
| POST | /api/documents | Neues Dokument anlegen (wird von der Scan-Pipeline aufgerufen) |
| PUT | /api/documents/{id} | Dokument aktualisieren (Tags, Typ editieren) |
| DELETE | /api/documents/{id} | Dokument löschen |
| GET | /api/tags | Alle Tags mit Dokumentanzahl |
| POST | /api/tags | Neuen Tag anlegen |
| GET | /api/documents/types | Alle Dokumenttypen |
| GET | /api/health | Health-Check |

POST /api/documents Body:
```json
{
  "title": "Rechnung Stadtwerke Mai 2026",
  "summary": "Rechnung der Stadtwerke fuer Strom und Gas",
  "original_filename": "scan_001.pdf",
  "stored_filename": "2026-05-20_rechnung-stadtwerke.pdf",
  "document_type": "Rechnung",
  "document_date": "2026-05-20",
  "nextcloud_path": "Rechnung/2026-05-20_rechnung-stadtwerke.pdf",
  "tags": ["rechnung", "stadtwerke", "strom", "haus"]
}
```

Die `nextcloud_url` wird serverseitig aus der Env-Variable `DOCARCHIV_NC_BASE_URL` + `nextcloud_path` zusammengebaut.

### Frontend-Screens

**Dokumentenliste (Hauptansicht):**
- Header mit App-Name und prominenter Suchleiste
- Filter-Leiste: Dokumenttyp-Chips, Datums-Range, aktive Tags
- Dokumenten-Karten im Grid (1-3 Spalten, responsive): Typ-Badge, Titel, Summary (2 Zeilen), Tags als Chips, Datum, Nextcloud-Link-Icon
- Tag-Cloud als Filter (Sidebar oder ausklappbar)
- Pagination

**Dokument-Detail (Drawer/Modal):**
- Vollständige Zusammenfassung
- Tags editierbar (Autocomplete)
- Dokumenttyp editierbar (Select)
- Datum, Original-Dateiname
- Primär-Button "In Nextcloud öffnen" (Grün)
- Löschen-Button mit Bestätigung

### DDD-Architektur (Domain-Driven Design)

Das Backend folgt einer **schlanken DDD-Schichtung**. Kein Over-Engineering, aber saubere Trennung:

```
backend/
├── main.py                     # FastAPI App-Factory, Startup, SPA-Serving
├── config.py                   # Pydantic Settings (Env-Variablen)
│
├── domain/                     # Domain Layer – reine Geschaeftslogik
│   ├── models.py               # SQLAlchemy ORM Models (Document, Tag, DocumentTag)
│   ├── schemas.py              # Pydantic Schemas (Request/Response DTOs)
│   └── services.py             # Business-Logik (Suche, Tag-Verwaltung, Nextcloud-URL-Builder)
│
├── api/                        # API Layer – HTTP-Schnittstelle
│   ├── dependencies.py         # FastAPI Dependencies (DB-Session, etc.)
│   ├── documents.py            # Document-Endpunkte (CRUD + Suche)
│   └── tags.py                 # Tag-Endpunkte
│
├── infrastructure/             # Infrastructure Layer – DB, externe Systeme
│   ├── database.py             # Engine, SessionLocal, Base
│   └── repositories.py         # Repository-Pattern: DB-Queries gekapselt
│
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
│
├── requirements.txt
└── tests/
    ├── conftest.py             # Fixtures, Test-DB (SQLite in-memory)
    ├── test_documents.py
    └── test_tags.py
```

**Schichten-Regeln:**
- `domain/` importiert NICHTS aus `api/` oder `infrastructure/` (ausser SQLAlchemy Base fuer Models)
- `api/` importiert aus `domain/` (Schemas, Services) und `infrastructure/` (Dependencies)
- `infrastructure/` importiert aus `domain/` (Models)
- Business-Logik lebt in `domain/services.py`, NICHT in den API-Endpunkten
- API-Endpunkte sind duenn: Request validieren → Service aufrufen → Response zurueckgeben

**Repository-Pattern:**
- `infrastructure/repositories.py` kapselt alle DB-Queries
- Services rufen Repositories auf, nicht direkt die DB-Session
- Das macht Tests einfacher (Repository mocken statt DB)

### Frontend-Struktur

```
frontend/src/
├── App.tsx                     # Router, Layout
├── main.tsx                    # Entry Point, MantineProvider mit Theme
├── theme.ts                    # EnBW Mantine Theme Override
│
├── api/
│   └── client.ts               # Typisierter Fetch-Client, Error-Handling
│
├── types/
│   └── document.ts             # TypeScript Interfaces (Document, Tag, etc.)
│
├── hooks/
│   ├── useDocuments.ts          # Dokumente laden, suchen, filtern
│   └── useTags.ts               # Tags laden
│
├── components/
│   ├── layout/
│   │   └── AppShell.tsx         # Header, Sidebar-Layout
│   ├── documents/
│   │   ├── DocumentList.tsx     # Grid mit Karten
│   │   ├── DocumentCard.tsx     # Einzelne Karte
│   │   └── DocumentDetail.tsx   # Detail-Drawer/Modal
│   ├── search/
│   │   ├── SearchBar.tsx        # Volltextsuche
│   │   └── FilterSidebar.tsx    # Tag-Filter, Typ-Filter, Datum
│   └── tags/
│       └── TagCloud.tsx         # Tag-Uebersicht mit Counts
│
└── pages/
    └── HomePage.tsx             # Hauptseite (DocumentList + Filter)
```

### Umgebungsvariablen (.env.example)

```
DATABASE_URL=postgresql://docarchiv:changeme@docarchiv-db:5432/docarchiv
DOCARCHIV_NC_BASE_URL=https://nextcloud.example.com/apps/files/?dir=/Documents/Scans
POSTGRES_USER=docarchiv
POSTGRES_PASSWORD=changeme
POSTGRES_DB=docarchiv
```

### Umsetzungsreihenfolge

1. **Backend:** FastAPI App, Domain Models + Schemas, Infrastructure (DB + Repositories), Domain Services, API-Endpunkte, Alembic Migration, PostgreSQL Volltextsuche, Tests
2. **Frontend:** Vite + React + Mantine Setup, EnBW-Theme, API-Client, Hooks, Components (DocumentList, DocumentCard, DocumentDetail, SearchBar, TagCloud, FilterSidebar)
3. **Docker:** Multi-Stage Dockerfile, docker-compose.yml mit PostgreSQL, FastAPI served statische SPA-Dateien

### Wichtige Regeln

**Allgemein:**
- Sprache: Dokumentation und Kommentare auf Deutsch, Code und Variablennamen auf Englisch
- Keine echten Secrets committen – nur Platzhalter in .env.example
- Commit-Messages: `<typ>: <beschreibung>` (z.B. `feat: document search endpoint`, `fix: tag count query`)

**Backend (Python):**
- Type Hints ueberall, Docstrings fuer Module und oeffentliche Funktionen
- Pydantic v2 fuer alle Request/Response Schemas (nicht dict)
- FastAPI Dependencies fuer DB-Session Injection
- Repository-Pattern: DB-Queries nur in `infrastructure/repositories.py`
- Business-Logik nur in `domain/services.py`, nicht in API-Endpunkten
- Alembic fuer DB-Migrations (nicht raw SQL)
- Tests mit pytest; Test-DB als SQLite in-memory oder PostgreSQL Testcontainer
- Error-Handling: HTTPException mit sinnvollen Status-Codes (404, 422, 500)
- Logging ueber Python `logging`-Modul

**Frontend (TypeScript/React):**
- TypeScript strict, keine `any`-Types
- Mantine v7 Komponenten bevorzugen (keine eigenen UI-Primitives bauen)
- Custom Hooks fuer Datenlogik (`useDocuments`, `useTags`)
- Fetch-basierter API-Client (kein axios)
- Komponenten klein halten, Single Responsibility
- Keine globalen State-Manager (React State + URL-Params reichen)

**Docker:**
- FastAPI served die gebaute SPA als statische Dateien aus `./static/`
- Multi-Stage Build: Node fuer Frontend → Python fuer Runtime
- Health-Check Endpoint `/api/health` muss immer funktionieren
