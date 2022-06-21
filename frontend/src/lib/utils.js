export function extractFileNameFromUrl(url) {
  return url.split("/").slice(-1)[0];
}
