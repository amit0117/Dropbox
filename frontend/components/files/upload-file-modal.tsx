"use client";

import { useMemo, useState } from "react";
import { Alert, Button, FileInput, Modal, Stack, Text } from "@mantine/core";
import { confirmUpload, getUploadUrl } from "@/lib/backend-api";
import {
  ALLOWED_MIME_TYPES,
  MAX_FILE_SIZE_BYTES,
  formatFileSize,
} from "@/lib/file-utils";
import {
  FILE_ACCEPTED_EXTENSIONS_BY_MIME,
  type AllowedMimeType,
} from "@/types/files";

interface UploadFileModalProps {
  opened: boolean;
  onClose: () => void;
  onUploaded: () => Promise<void> | void;
}

export function UploadFileModal({
  opened,
  onClose,
  onUploaded,
}: UploadFileModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const accept = useMemo(() => FILE_ACCEPTED_EXTENSIONS_BY_MIME, []);

  const resetState = () => {
    setFile(null);
    setError(null);
    setIsUploading(false);
  };

  const validateFile = (selectedFile: File): string | null => {
    if (!ALLOWED_MIME_TYPES.includes(selectedFile.type as AllowedMimeType)) {
      return `Unsupported file type: ${selectedFile.type}`;
    }

    if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
      return `File too large. Max allowed size is ${formatFileSize(MAX_FILE_SIZE_BYTES)}.`;
    }
    return null;
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsUploading(true);
    setError(null);
    let createdFileId: string | null = null;
    try {
      const uploadData = await getUploadUrl({
        name: file.name,
        size_bytes: file.size,
        mime_type: file.type as AllowedMimeType,
      });

      createdFileId = uploadData.file_id;

      const UPLOAD_PUT_TIMEOUT_MS = 120_000; // 2 min for large files
      const uploadController = new AbortController();
      const uploadTimeoutId = setTimeout(
        () => uploadController.abort(),
        UPLOAD_PUT_TIMEOUT_MS,
      );
      let uploadResponse: Response;
      try {
        uploadResponse = await fetch(uploadData.upload_url, {
          method: "PUT",
          headers: {
            "Content-Type": file.type,
          },
          body: file,
          signal: uploadController.signal,
        });
      } finally {
        clearTimeout(uploadTimeoutId);
      }

      if (!uploadResponse.ok) {
        throw new Error(`Upload to storage failed (${uploadResponse.status}).`);
      }

      await confirmUpload(uploadData.file_id, { status: "uploaded" });
      await onUploaded();
      resetState();
      onClose();
    } catch (uploadError) {
      if (createdFileId) {
        try {
          await confirmUpload(createdFileId, { status: "failed" });
        } catch {
          // Ignore failure confirmation errors to preserve original upload error.
        }
      }
      const message =
        uploadError instanceof Error && uploadError.name === "AbortError" ?
          "Upload timed out. Try a smaller file or check your connection."
        : uploadError instanceof Error ? uploadError.message
        : "Upload failed.";
      setError(message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Modal
      centered
      onClose={() => {
        resetState();
        onClose();
      }}
      opened={opened}
      title="Upload file"
      styles={{
        title: { color: "var(--mantine-color-gray-0)", fontWeight: 600 },
      }}
    >
      <Stack>
        <Text c="gray.3" size="sm">
          Supported formats: txt, json, jpg, jpeg, png, pdf. Max file size:{" "}
          {formatFileSize(MAX_FILE_SIZE_BYTES)}.
        </Text>
        <FileInput
          accept={Object.values(accept).flat().join(",")}
          label="Select file"
          onChange={setFile}
          placeholder="Pick one file"
          styles={{ label: { color: "var(--mantine-color-gray-0)" } }}
        />
        {error ?
          <Alert color="red" title="Upload error">
            {error}
          </Alert>
        : null}
        <Button loading={isUploading} onClick={handleUpload}>
          Upload
        </Button>
      </Stack>
    </Modal>
  );
}
