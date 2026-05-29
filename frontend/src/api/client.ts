import type {
  AdminStatsResponse,
  Correspondent,
  CreateCorrespondentPayload,
  CreateDocumentPayload,
  CreateDocumentTypePayload,
  CreateTagPayload,
  DatabaseInfoResponse,
  DocumentDetail,
  DocumentListQuery,
  DocumentSummary,
  DocumentTypeInfo,
  PaginatedResponse,
  ResetDatabaseResponse,
  Tag,
  UpdateCorrespondentPayload,
  UpdateDocumentPayload,
  UpdateDocumentTypePayload,
  UpdateTagPayload,
} from '../types/document';

const API_BASE_PATH = '/api';

export class ApiError extends Error {
  public readonly status: number;

  public readonly details: unknown;

  public constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function request<TResponse>(path: string, init: RequestInit = {}): Promise<TResponse> {
  const response = await fetch(`${API_BASE_PATH}${path}`, {
    headers: {
      Accept: 'application/json',
      ...jsonHeaders(init.body),
      ...init.headers,
    },
    ...init,
  });

  if (response.status === 204) {
    return undefined as TResponse;
  }

  const payload: unknown = await parseJson(response);

  if (!response.ok) {
    throw new ApiError(extractErrorMessage(payload, response.statusText), response.status, payload);
  }

  return payload as TResponse;
}

function jsonHeaders(body: BodyInit | null | undefined): HeadersInit {
  if (typeof body === 'string') {
    return { 'Content-Type': 'application/json' };
  }

  return {};
}

async function parseJson(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

function extractErrorMessage(payload: unknown, fallback: string): string {
  if (isRecord(payload) && typeof payload.detail === 'string') {
    return payload.detail;
  }

  if (isRecord(payload) && Array.isArray(payload.detail)) {
    return 'Die API-Anfrage enthaelt ungueltige Daten.';
  }

  return fallback || 'Die API-Anfrage ist fehlgeschlagen.';
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function toQueryString(query: DocumentListQuery): string {
  const params = new URLSearchParams();

  appendStringParam(params, 'q', query.q);
  appendNumberParam(params, 'document_type_id', query.document_type_id);
  appendNumberParam(params, 'correspondent_id', query.correspondent_id);
  appendStringParam(params, 'date_from', query.date_from);
  appendStringParam(params, 'date_to', query.date_to);
  appendNumberParam(params, 'page', query.page);
  appendNumberParam(params, 'per_page', query.per_page);
  appendStringParam(params, 'sort', query.sort);

  if (query.tags !== undefined && query.tags.length > 0) {
    params.set('tags', query.tags.join(','));
  }

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

function appendStringParam(params: URLSearchParams, key: string, value: string | undefined): void {
  const normalized = value?.trim();

  if (normalized) {
    params.set(key, normalized);
  }
}

function appendNumberParam(params: URLSearchParams, key: string, value: number | undefined): void {
  if (value !== undefined) {
    params.set(key, String(value));
  }
}

export const apiClient = {
  getHealth(): Promise<{ status: string; service: string; version: string }> {
    return request('/health');
  },

  // --- Dokumente ---

  listDocuments(query: DocumentListQuery = {}): Promise<PaginatedResponse<DocumentSummary>> {
    return request(`/documents${toQueryString(query)}`);
  },

  getDocument(documentId: number): Promise<DocumentDetail> {
    return request(`/documents/${documentId}`);
  },

  createDocument(payload: CreateDocumentPayload): Promise<DocumentDetail> {
    return request('/documents', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  updateDocument(documentId: number, payload: UpdateDocumentPayload): Promise<DocumentDetail> {
    return request(`/documents/${documentId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  deleteDocument(documentId: number): Promise<void> {
    return request(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  },

  // --- Tags ---

  listTags(): Promise<Tag[]> {
    return request('/tags');
  },

  createTag(payload: CreateTagPayload): Promise<Tag> {
    return request('/tags', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getTag(tagId: number): Promise<Tag> {
    return request(`/tags/${tagId}`);
  },

  deleteTag(tagId: number): Promise<void> {
    return request(`/tags/${tagId}`, {
      method: 'DELETE',
    });
  },

  updateTag(tagId: number, payload: UpdateTagPayload): Promise<Tag> {
    return request(`/tags/${tagId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  // --- Korrespondenten ---

  listCorrespondents(): Promise<Correspondent[]> {
    return request('/correspondents');
  },

  createCorrespondent(payload: CreateCorrespondentPayload): Promise<Correspondent> {
    return request('/correspondents', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getCorrespondent(correspondentId: number): Promise<Correspondent> {
    return request(`/correspondents/${correspondentId}`);
  },

  updateCorrespondent(correspondentId: number, payload: UpdateCorrespondentPayload): Promise<Correspondent> {
    return request(`/correspondents/${correspondentId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  deleteCorrespondent(correspondentId: number): Promise<void> {
    return request(`/correspondents/${correspondentId}`, {
      method: 'DELETE',
    });
  },

  // --- Dokumenttypen ---

  listDocumentTypes(): Promise<DocumentTypeInfo[]> {
    return request('/document-types');
  },

  createDocumentType(payload: CreateDocumentTypePayload): Promise<DocumentTypeInfo> {
    return request('/document-types', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getDocumentType(documentTypeId: number): Promise<DocumentTypeInfo> {
    return request(`/document-types/${documentTypeId}`);
  },

  updateDocumentType(documentTypeId: number, payload: UpdateDocumentTypePayload): Promise<DocumentTypeInfo> {
    return request(`/document-types/${documentTypeId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  deleteDocumentType(documentTypeId: number): Promise<void> {
    return request(`/document-types/${documentTypeId}`, {
      method: 'DELETE',
    });
  },

  // --- Admin ---

  getAdminStats(): Promise<AdminStatsResponse> {
    return request('/admin/stats');
  },

  getDatabaseInfo(): Promise<DatabaseInfoResponse> {
    return request('/admin/database-info');
  },

  resetDatabase(): Promise<ResetDatabaseResponse> {
    return request('/admin/reset-database', {
      method: 'POST',
    });
  },
};
