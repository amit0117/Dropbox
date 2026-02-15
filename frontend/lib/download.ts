export async function downloadFileFromS3(
  url: string,
  filename: string,
): Promise<void> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to download file: ${response.statusText}`);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  // We want that onclick of the download link, the file is downloaded to the user's machine
  // So we need to create a temporary link and click it programmatically
  const a = document.createElement("a");
  a.style.display = "none";
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();

  setTimeout(() => {
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(a);
  }, 100);
}
