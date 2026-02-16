import { createClient } from "@/utils/supabase/client";
import type {
  ConfirmUploadRequest,
  ConfirmUploadResponse,
  DownloadUrlResponse,
  FileListResponse,
  UploadUrlRequest,
  UploadUrlResponse,
} from "@/types/files";

const DEFAULT_REQUEST_MS =5* 60* 1000;

const getBackendBaseUrl = () => {
  const value = process.env.NEXT_PUBLIC_API_URL;

  if (!value) {
    throw new Error("Missing NEXT_PUBLIC_BACKEND_API_URL");
  }

  return value.replace(/\/+$/, "");
};

const fetchWithTimeout = async (
  url: string,
  init: RequestInit,
  timeoutMs = DEFAULT_REQUEST_MS,
): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal, // Abort the request if it takes too long
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
};

const getAccessToken = async () => {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const token = session?.access_token;

  if (!token) {
    throw new Error("User is not authenticated");
  }

  return token;
};

const apiFetch = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const token = await getAccessToken();
  const url = `${getBackendBaseUrl()}${path}`;
  let response: Response;
  try {
    response = await fetchWithTimeout(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...(init?.headers || {}),
      },
    });
  } catch (err) {
    console.error("Error fetching from backend:", err);
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Request timed out");
    }
    throw new Error(
      err instanceof Error ?
        err.message
      : "Something went wrong. Please try again later.",
    );
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
};

export const listFiles = (skip = 0, limit = 20) => {
  return apiFetch<FileListResponse>(
    `/api/v1/files?skip=${skip}&limit=${limit}`,
  );
};

export const getUploadUrl = (payload: UploadUrlRequest) => {
  return apiFetch<UploadUrlResponse>("/api/v1/files/upload-url", {
    method: "POST",
    body: JSON.stringify(payload),
  });
};

export const confirmUpload = (
  fileId: string,
  payload: ConfirmUploadRequest,
) => {
  return apiFetch<ConfirmUploadResponse>(`/api/v1/files/${fileId}/confirm`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
};

export const getDownloadUrl = (fileId: string) => {
  return apiFetch<DownloadUrlResponse>(`/api/v1/files/${fileId}/download-url`);
};

export const deleteFile = async (fileId: string): Promise<void> => {
  return apiFetch<void>(`/api/v1/files/${fileId}`, {
    method: "DELETE",
  });
};
