"use client";

import { Button, Group, Table, Text } from "@mantine/core";
import type { UserFile } from "@/types/files";
import { formatDateTimeInIST, formatFileSize } from "@/lib/file-utils";

interface FilesTableProps {
  files: UserFile[];
  onDownload: (file: UserFile) => void;
  onDelete: (file: UserFile) => void;
  downloadingId?: string | null;
  deletingId?: string | null;
}

export function FilesTable({
  files,
  onDownload,
  onDelete,
  downloadingId,
  deletingId,
}: FilesTableProps) {
  return (
    <Table highlightOnHover striped withColumnBorders>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>File name</Table.Th>
          <Table.Th>Type</Table.Th>
          <Table.Th>Size</Table.Th>
          <Table.Th>Uploaded at</Table.Th>
          <Table.Th>Actions</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {files.length === 0 ? (
          <Table.Tr>
            <Table.Td colSpan={5}>
              <Text c="dimmed" ta="center">
                No files uploaded yet.
              </Text>
            </Table.Td>
          </Table.Tr>
        ) : (
          files.map((file) => (
            <Table.Tr
              key={file.id}
              style={{ cursor: "pointer" }}
            >
              <Table.Td>{file.name}</Table.Td>
              <Table.Td>{file.mime_type}</Table.Td>
              <Table.Td>{formatFileSize(file.size_bytes)}</Table.Td>
              <Table.Td>{formatDateTimeInIST(file.created_at)}</Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Button
                    aria-label={`Download ${file.name}`}
                    loading={downloadingId === file.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      onDownload(file);
                    }}
                    size="xs"
                    variant="light"
                  >
                    Download
                  </Button>
                  <Button
                    aria-label={`Delete ${file.name}`}
                    color="red"
                    loading={deletingId === file.id}
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(file);
                    }}
                    size="xs"
                    variant="light"
                  >
                    Delete
                  </Button>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))
        )}
      </Table.Tbody>
    </Table>
  );
}
