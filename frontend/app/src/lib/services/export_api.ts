import { request } from '$lib/utils/request';

export async function exportAsJson(token: string): Promise<Blob> {
	return request<Blob>('/export/json', {
		headers: {
			Authorization: `Bearer ${token}`
		},
		responseType: 'blob',
		fallbackError: 'Export failed'
	});
}

export async function exportAsCsv(token: string): Promise<Blob> {
	return request<Blob>('/export/csv', {
		headers: {
			Authorization: `Bearer ${token}`
		},
		responseType: 'blob',
		fallbackError: 'Export failed'
	});
}

export function downloadBlob(blob: Blob, filename: string): void {
	const url = globalThis.URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	a.remove();
	globalThis.URL.revokeObjectURL(url);
}
