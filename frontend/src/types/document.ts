export interface Correspondent {
  id: number;
  name: string;
  document_count: number;
}

export interface DocumentTypeInfo {
  id: number;
  name: string;
  color: string | null;
  document_count: number;
}

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
  document_type_id: number;
  correspondent_id: number | null;
  document_date: string | null;
  nextcloud_path: string;
  nextcloud_url: string;
  created_at: string;
  updated_at: string;
  document_type: DocumentTypeInfo;
  correspondent: Correspondent | null;
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
  document_type_id?: number;
  correspondent_id?: number;
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
  document_type_id: number;
  correspondent_id: number | null;
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

export interface CreateCorrespondentPayload {
  name: string;
}

export interface UpdateCorrespondentPayload {
  name?: string;
}

export interface CreateDocumentTypePayload {
  name: string;
  color?: string | null;
}

export interface UpdateDocumentTypePayload {
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

export interface TypeCount {
  name: string;
  count: number;
}

export interface CorrespondentCount {
  name: string;
  count: number;
}

export interface AdminStatsResponse {
  total_documents: number;
  total_tags: number;
  total_correspondents: number;
  total_document_types: number;
  documents_by_type: TypeCount[];
  documents_by_month: MonthCount[];
  top_tags: TagCount[];
  top_correspondents: CorrespondentCount[];
  documents_without_tags: number;
  documents_without_correspondent: number;
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
  deleted_correspondents: number;
  deleted_document_types: number;
}
