import { FileMimeType, type AllowedMimeType } from "@/types/files";

export const ALLOWED_MIME_TYPES: AllowedMimeType[] = [
  FileMimeType.TEXT_PLAIN,
  FileMimeType.IMAGE_JPEG,
  FileMimeType.IMAGE_PNG,
  FileMimeType.APPLICATION_JSON,
  FileMimeType.APPLICATION_PDF,
];

export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

export const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

export const formatDateTimeInIST = (isoDate: string) => {
  const date = new Date(isoDate);

  const parts = new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).formatToParts(date);

  const lookup = Object.fromEntries(
    parts.map((part) => [part.type, part.value]),
  );
  return `${lookup.day}-${lookup.month}-${lookup.year}, ${lookup.hour}:${lookup.minute} ${lookup.dayPeriod}`;
};
