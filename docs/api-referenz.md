# DocArchiv API-Referenz

> **Base-URL:** `http://localhost:8088/api`
>
> **OpenAPI-Spec:** [`docs/openapi.json`](../docs/openapi.json) – kann in Swagger-UI oder Redoc importiert werden.
>
> Die interaktive Swagger-UI ist unter `http://localhost:8088/docs` erreichbar.

---

## Inhaltsverzeichnis

1. [Archiv befuellen – Workflow](#archiv-befuellen--workflow)
2. [Korrespondenten](#korrespondenten)
3. [Dokumenttypen](#dokumenttypen)
4. [Tags](#tags)
5. [Dokumente](#dokumente)
6. [Admin](#admin)
7. [Health](#health)

---

## Archiv befuellen – Workflow

Um das Archiv mit Dokumenten zu befuellen, ist folgende Reihenfolge empfohlen:

```
1. Dokumenttypen anlegen   POST /api/document-types
2. Korrespondenten anlegen POST /api/correspondents
3. Dokumente anlegen       POST /api/documents  (Tags werden automatisch erstellt)
```

### Beispiel: Kompletter Import per curl

```bash
# 1. Dokumenttyp anlegen
curl -X POST http://localhost:8088/api/document-types \
  -H "Content-Type: application/json" \
  -d '{"name": "Rechnung", "color": "#e74c3c"}'
# → {"id": 1, "name": "Rechnung", "color": "#e74c3c", "document_count": 0}

# 2. Korrespondent anlegen
curl -X POST http://localhost:8088/api/correspondents \
  -H "Content-Type: application/json" \
  -d '{"name": "Stadtwerke München"}'
# → {"id": 1, "name": "Stadtwerke München", "document_count": 0}

# 3. Dokument anlegen (Tags werden automatisch per get-or-create aufgeloest)
curl -X POST http://localhost:8088/api/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Stromrechnung Januar 2025",
    "summary": "Monatliche Abrechnung Strom",
    "original_filename": "stromrechnung_2025_01.pdf",
    "stored_filename": "2025/01/stromrechnung_2025_01.pdf",
    "document_type_id": 1,
    "correspondent_id": 1,
    "document_date": "2025-01-15",
    "nextcloud_path": "Dokumente/Rechnungen/2025/stromrechnung_2025_01.pdf",
    "tags": ["strom", "2025", "monatlich"]
  }'
```

> **Hinweis:** Dokumenttypen und Korrespondenten muessen **vor** dem Dokument existieren. Tags werden beim Dokument-Erstellen automatisch angelegt, falls sie noch nicht existieren.

---

## Korrespondenten

Korrespondenten sind Absender oder Empfaenger von Dokumenten (z.B. Firmen, Behoerden, Personen).

### `GET /api/correspondents`

Listet alle Korrespondenten mit Dokumentanzahl.

**Response:** `200 OK`
```json
[
  {"id": 1, "name": "Stadtwerke München", "document_count": 5},
  {"id": 2, "name": "Finanzamt", "document_count": 12}
]
```

### `POST /api/correspondents`

Erstellt einen neuen Korrespondenten. Falls der Name bereits existiert, wird der bestehende zurueckgegeben.

**Request-Body:**
| Feld   | Typ    | Pflicht | Beschreibung          |
|--------|--------|---------|-----------------------|
| `name` | string | ja      | Name (max. 255 Zeichen) |

**Response:** `201 Created`
```json
{"id": 3, "name": "Deutsche Post", "document_count": 0}
```

### `GET /api/correspondents/{correspondent_id}`

Liefert einen einzelnen Korrespondenten.

**Response:** `200 OK` oder `404 Not Found`

### `PATCH /api/correspondents/{correspondent_id}`

Aktualisiert den Namen eines Korrespondenten.

**Request-Body:**
| Feld   | Typ           | Pflicht | Beschreibung |
|--------|---------------|---------|--------------|
| `name` | string \| null | nein    | Neuer Name   |

**Response:** `200 OK` oder `404 Not Found`

### `DELETE /api/correspondents/{correspondent_id}`

Loescht einen Korrespondenten. Schlaegt fehl, wenn noch Dokumente zugeordnet sind (FK-Constraint).

**Response:** `204 No Content` oder `404 Not Found`

---

## Dokumenttypen

Dokumenttypen kategorisieren Dokumente (z.B. Rechnung, Vertrag, Antrag).

### `GET /api/document-types`

Listet alle Dokumenttypen mit Dokumentanzahl.

**Response:** `200 OK`
```json
[
  {"id": 1, "name": "Rechnung", "color": "#e74c3c", "document_count": 8},
  {"id": 2, "name": "Vertrag", "color": "#2ecc71", "document_count": 3}
]
```

### `POST /api/document-types`

Erstellt einen neuen Dokumenttyp. Falls der Name bereits existiert, wird der bestehende zurueckgegeben.

**Request-Body:**
| Feld    | Typ           | Pflicht | Beschreibung                    |
|---------|---------------|---------|---------------------------------|
| `name`  | string        | ja      | Name (max. 100 Zeichen)         |
| `color` | string \| null | nein    | Hex-Farbe, z.B. `"#e74c3c"`    |

**Response:** `201 Created`
```json
{"id": 3, "name": "Antrag", "color": "#3498db", "document_count": 0}
```

### `GET /api/document-types/{document_type_id}`

Liefert einen einzelnen Dokumenttyp.

### `PATCH /api/document-types/{document_type_id}`

Aktualisiert Name und/oder Farbe.

**Request-Body:**
| Feld    | Typ           | Pflicht | Beschreibung |
|---------|---------------|---------|--------------|
| `name`  | string \| null | nein    | Neuer Name   |
| `color` | string \| null | nein    | Neue Farbe   |

### `DELETE /api/document-types/{document_type_id}`

Loescht einen Dokumenttyp. Schlaegt fehl, wenn noch Dokumente zugeordnet sind (FK-Constraint `RESTRICT`).

**Response:** `204 No Content` oder `404 Not Found`

---

## Tags

Tags sind frei vergebbare Schlagwoerter fuer Dokumente (M:N-Beziehung).

### `GET /api/tags`

Listet alle Tags mit Dokumentanzahl.

**Response:** `200 OK`
```json
[
  {"id": 1, "name": "strom", "color": "#f39c12", "document_count": 3},
  {"id": 2, "name": "2025", "color": null, "document_count": 10}
]
```

### `POST /api/tags`

Erstellt einen neuen Tag. Falls der Name bereits existiert, wird der bestehende zurueckgegeben.

**Request-Body:**
| Feld    | Typ           | Pflicht | Beschreibung                 |
|---------|---------------|---------|------------------------------|
| `name`  | string        | ja      | Name (max. 80 Zeichen)       |
| `color` | string \| null | nein    | Hex-Farbe, z.B. `"#f39c12"` |

**Response:** `201 Created`

### `GET /api/tags/{tag_id}` · `PATCH /api/tags/{tag_id}` · `DELETE /api/tags/{tag_id}`

Standard-CRUD analog zu Korrespondenten.

---

## Dokumente

### `GET /api/documents`

Listet Dokumente mit Suche, Filtern, Pagination und Sortierung.

**Query-Parameter:**
| Parameter          | Typ     | Default      | Beschreibung                                    |
|--------------------|---------|--------------|-------------------------------------------------|
| `q`                | string  | –            | Volltextsuche (PostgreSQL TSVECTOR)              |
| `tags`             | string  | –            | Kommaseparierte Tag-Namen, z.B. `strom,2025`     |
| `document_type_id` | integer | –            | Filtert nach Dokumenttyp-ID                      |
| `correspondent_id` | integer | –            | Filtert nach Korrespondent-ID                    |
| `date_from`        | date    | –            | Dokumente ab diesem Datum (YYYY-MM-DD)           |
| `date_to`          | date    | –            | Dokumente bis zu diesem Datum (YYYY-MM-DD)       |
| `sort`             | string  | `date_desc`  | Sortierung: `date_desc`, `date_asc`, `title_asc`, `title_desc`, `relevance` |
| `page`             | integer | `1`          | Seitennummer                                     |
| `per_page`         | integer | `20`         | Eintraege pro Seite (max. 100)                   |

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "title": "Stromrechnung Januar 2025",
      "summary": "Monatliche Abrechnung Strom",
      "original_filename": "stromrechnung_2025_01.pdf",
      "stored_filename": "2025/01/stromrechnung_2025_01.pdf",
      "document_type_id": 1,
      "correspondent_id": 1,
      "document_date": "2025-01-15",
      "nextcloud_path": "Dokumente/Rechnungen/2025/stromrechnung_2025_01.pdf",
      "nextcloud_url": "https://cloud.example.com/apps/files/?dir=/Dokumente/Rechnungen/2025&openfile=stromrechnung_2025_01.pdf",
      "created_at": "2025-01-20T10:30:00",
      "updated_at": "2025-01-20T10:30:00",
      "document_type": {"id": 1, "name": "Rechnung", "color": "#e74c3c"},
      "correspondent": {"id": 1, "name": "Stadtwerke München"},
      "tags": [
        {"id": 1, "name": "strom", "color": "#f39c12"},
        {"id": 2, "name": "2025", "color": null}
      ]
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

### `POST /api/documents`

Erstellt ein neues Dokument. Tags werden per get-or-create aufgeloest.

**Request-Body:**
| Feld                | Typ           | Pflicht | Beschreibung                                |
|---------------------|---------------|---------|---------------------------------------------|
| `title`             | string        | ja      | Dokumenttitel (max. 255 Zeichen)            |
| `summary`           | string        | nein    | Zusammenfassung / Beschreibung              |
| `original_filename` | string        | ja      | Originaler Dateiname                        |
| `stored_filename`   | string        | ja      | Gespeicherter Dateiname in Nextcloud        |
| `document_type_id`  | integer       | ja      | ID des Dokumenttyps (muss existieren)       |
| `correspondent_id`  | integer \| null | nein   | ID des Korrespondenten (muss existieren)    |
| `document_date`     | date \| null   | nein   | Dokumentdatum (YYYY-MM-DD)                  |
| `nextcloud_path`    | string        | ja      | Relativer Nextcloud-Pfad **oder** kompletter `http(s)`-Nextcloud-Link |
| `tags`              | string[]      | nein    | Tag-Namen (werden automatisch angelegt)     |

**Response:** `201 Created` – Vollstaendiges Dokument-Objekt (siehe GET-Response)

Beispiel mit komplettem Nextcloud-Link:

```json
{
  "title": "Stromrechnung Februar 2025",
  "summary": "Abrechnung Strom",
  "original_filename": "stromrechnung_2025_02.pdf",
  "stored_filename": "2025/02/stromrechnung_2025_02.pdf",
  "document_type_id": 1,
  "correspondent_id": 1,
  "document_date": "2025-02-14",
  "nextcloud_path": "https://nextcloud.example.com/apps/files/?dir=/Dokumente/Rechnungen/2025&file=stromrechnung_2025_02.pdf",
  "tags": ["strom", "2025"]
}
```

Hinweis: Bei einer kompletten URL nutzt DocArchiv diese URL direkt als `nextcloud_url` und leitet daraus einen darstellbaren `nextcloud_path` fuer die UI ab.

### `GET /api/documents/{document_id}`

Liefert ein einzelnes Dokument mit allen Details.

**Response:** `200 OK` oder `404 Not Found`

### `PUT /api/documents/{document_id}`

Aktualisiert ein Dokument (Partial Update). Nur uebergebene Felder werden geaendert.

**Request-Body:** Alle Felder optional (siehe `DocumentUpdate`-Schema).

> **Achtung bei Tags:** Wenn `tags` uebergeben wird, ersetzt die Liste die bisherigen Tags komplett.

**Response:** `200 OK` oder `404 Not Found`

### `DELETE /api/documents/{document_id}`

Loescht ein Dokument.

**Response:** `204 No Content` oder `404 Not Found`

---

## Admin

### `GET /api/admin/stats`

Liefert Dashboard-Statistiken.

**Response:** `200 OK`
```json
{
  "total_documents": 42,
  "total_tags": 15,
  "total_correspondents": 8,
  "total_document_types": 5,
  "documents_by_type": [
    {"name": "Rechnung", "count": 20},
    {"name": "Vertrag", "count": 12}
  ],
  "documents_by_month": [
    {"month": "2025-01", "count": 8},
    {"month": "2025-02", "count": 5}
  ],
  "top_tags": [
    {"name": "2025", "count": 30},
    {"name": "strom", "count": 12}
  ],
  "top_correspondents": [
    {"name": "Stadtwerke München", "count": 5},
    {"name": "Finanzamt", "count": 12}
  ],
  "documents_without_tags": 3,
  "documents_without_correspondent": 7,
  "orphaned_tags": 1
}
```

### `GET /api/admin/database-info`

Liefert technische Datenbank-Informationen (Groesse, Tabellen, Alembic-Revision).

### `POST /api/admin/reset-database`

Loescht alle Daten (Dokumente, Tags, Korrespondenten, Dokumenttypen). **Nur fuer Entwicklung!**

**Response:** `200 OK`
```json
{
  "message": "Datenbank wurde zurueckgesetzt.",
  "deleted_documents": 42,
  "deleted_tags": 15,
  "deleted_correspondents": 8,
  "deleted_document_types": 5
}
```

---

## Health

### `GET /api/health`

Health-Check fuer Docker/Monitoring.

**Response:** `200 OK`
```json
{"status": "ok"}
```

---

## Fehlerbehandlung

Alle Endpunkte liefern bei Fehlern ein einheitliches Format:

| HTTP-Status | Bedeutung                          |
|-------------|------------------------------------|
| `400`       | Ungueltige Anfrage                 |
| `404`       | Ressource nicht gefunden           |
| `422`       | Validierungsfehler (Pydantic)      |
| `500`       | Interner Serverfehler              |

**Beispiel 422:**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```
