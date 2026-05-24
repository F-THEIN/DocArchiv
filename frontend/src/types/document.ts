export interface Tag {
  id: number;
  name: string;
  color: string | null;
  document_count: number;
}

export interface DocumentSummary {
  id: number;
  title: string;
  summary: string;
  original_filename: string;
  stored_filename: string;
  document_type: string;
  document_date: string | null;
  nextcloud_path: string;
  nextcloud_url: string;
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface DocumentDetail extends DocumentSummary {}

export interface PaginatedResponse<TItem> {
  items: TItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface DocumentListQuery {
  q?: string;
  tags?: string[];
  type?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  per_page?: number;
  sort?: DocumentSort;
}

export type DocumentSort = 'date_desc' | 'date_asc' | 'title_asc' | 'title_desc' | 'created_desc';

export interface DocumentFormValues {
  title: string;
  summary: string;
  original_filename: string;
  stored_filename: string;
  document_type: string;
  document_date: string | null;
  nextcloud_path: string;
  tags: string[];
}

export interface CreateDocumentPayload extends DocumentFormValues {}

export type UpdateDocumentPayload = Partial<DocumentFormValues>;

export interface CreateTagPayload {
  name: string;
  color?: string | null;
}

export interface UpdateTagPayload {
  name?: string;
  color?: string | null;
}

export interface MonthCount {
  month: string;
  count: number;
}

export interface TagCount {
  name: string;
  count: number;
}

export interface AdminStatsResponse {
  total_documents: number;
  total_tags: number;
  documents_by_type: Record<string, number>;
  documents_by_month: MonthCount[];
  top_tags: TagCount[];
  documents_without_tags: number;
  orphaned_tags: number;
}

export interface TableInfo {
  name: string;
  row_count: number;
  size: string;
}

export interface DatabaseInfoResponse {
  database_size: string;
  tables: TableInfo[];
  alembic_revision: string | null;
  postgres_version: string;
}

export interface ResetDatabaseResponse {
  message: string;
  deleted_documents: number;
  deleted_tags: number;
}
