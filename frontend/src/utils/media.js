import { getApiBaseUrl } from '../api/config';

export function resolveMediaUrl(image) {
  if (!image) return null;
  if (typeof image !== 'string') return null;
  if (image.startsWith('http://') || image.startsWith('https://')) {
    return image;
  }

  const baseUrl = getApiBaseUrl();
  if (image.startsWith('/')) {
    return `${baseUrl}${image}`;
  }

  return `${baseUrl}/media/${image}`;
}
