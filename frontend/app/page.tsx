"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Alert,
  AppShell,
  Button,
  Group,
  Loader,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { FilesTable } from "@/components/files/files-table";
import { UploadFileModal } from "@/components/files/upload-file-modal";
import { deleteFile, getDownloadUrl, listFiles } from "@/lib/backend-api";
import { downloadFileFromS3 } from "@/lib/download";
import type { UserFile } from "@/types/files";
import { createClient } from "@/utils/supabase/client";

export default function Home() {
  const router = useRouter();
  const [files, setFiles] = useState<UserFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadFiles = async () => {
    try {
      setError(null);
      const response = await listFiles(0, 20);
      setFiles(response.files);
    } catch (loadError) {
      setError(
        loadError instanceof Error ?
          loadError.message
        : "Failed to load files.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleDownload = async (file: UserFile) => {
    try {
      setError(null);
      setDownloadingId(file.id);
      const { download_url } = await getDownloadUrl(file.id);
      await downloadFileFromS3(download_url, file.name);
    } catch (downloadError) {
      setError(
        downloadError instanceof Error ?
          downloadError.message
        : "Failed to download file.",
      );
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDelete = async (file: UserFile) => {
    if (!confirm(`Delete "${file.name}"? This cannot be undone.`)) return;
    try {
      setError(null);
      setDeletingId(file.id);
      await deleteFile(file.id);
      await loadFiles();
    } catch (deleteError) {
      setError(
        deleteError instanceof Error ?
          deleteError.message
        : "Failed to delete file.",
      );
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
  };

  return (
    <AppShell padding="md">
      <AppShell.Header p="md" style={{ borderBottomWidth: 1 }}>
        <Group justify="space-between">
          <Title order={3} c="var(--mantine-color-gray-0)">
            Sample Dropbox
          </Title>
          <Group>
            <Button onClick={() => setUploadOpen(true)} variant="filled">
              + Upload
            </Button>
            <Button onClick={handleLogout} variant="default">
              Logout
            </Button>
          </Group>
        </Group>
      </AppShell.Header>
      <AppShell.Main pt={80}>
        <Stack>
          {error && files.length > 0 ?
            <Alert color="red">{error}</Alert>
          : null}
          {loading ?
            <Group justify="center" py="xl">
              <Loader />
              <Text>Loading files...</Text>
            </Group>
          : error ?
            <Group justify="center" py="xl">
              <Stack align="center" gap="md">
                <Text c="red" size="sm">
                  {error}
                </Text>
                <Button
                  onClick={() => {
                    setLoading(true);
                    void loadFiles();
                  }}
                  variant="light"
                >
                  Retry
                </Button>
              </Stack>
            </Group>
          : <FilesTable
              deletingId={deletingId}
              downloadingId={downloadingId}
              files={files}
              onDelete={handleDelete}
              onDownload={handleDownload}
            />
          }
        </Stack>
      </AppShell.Main>
      <UploadFileModal
        onClose={() => setUploadOpen(false)}
        onUploaded={loadFiles}
        opened={uploadOpen}
      />
    </AppShell>
  );
}
