export enum FileMimeType {
  TEXT_PLAIN = "text/plain",
  IMAGE_JPEG = "image/jpeg",
  IMAGE_PNG = "image/png",
  APPLICATION_JSON = "application/json",
  APPLICATION_PDF = "application/pdf",
}

export type AllowedMimeType = `${FileMimeType}`;

export const FILE_ACCEPTED_EXTENSIONS_BY_MIME: Record<AllowedMimeType, string[]> = {
  [FileMimeType.TEXT_PLAIN]: [".txt"],
  [FileMimeType.APPLICATION_JSON]: [".json"],
  [FileMimeType.IMAGE_JPEG]: [".jpg", ".jpeg"],
  [FileMimeType.IMAGE_PNG]: [".png"],
  [FileMimeType.APPLICATION_PDF]: [".pdf"],
};

export interface UserFile {
  id: string;
  user_id: string;
  name: string;
  storage_path: string;
  size_bytes: number;
  mime_type: AllowedMimeType;
  status: "uploading" | "uploaded" | "failed";
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface FileListResponse {
  files: UserFile[];
  total: number;
  skip: number;
  limit: number;
}

export interface UploadUrlRequest {
  name: string;
  size_bytes: number;
  mime_type: AllowedMimeType;
}

export interface UploadUrlResponse {
  file_id: string;
  upload_url: string;
  storage_path: string;
}

export interface ConfirmUploadRequest {
  status: "uploaded" | "failed";
}

export interface ConfirmUploadResponse {
  file_id: string;
  status: "uploaded" | "failed";
}

export interface DownloadUrlResponse {
  file_id: string;
  download_url: string;
  expires_in: number;
}
