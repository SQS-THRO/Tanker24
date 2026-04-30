import { env } from '$env/dynamic/public';

const API_BASE = (env.PUBLIC_BACKEND_URL ?? 'http://127.0.0.1:8000') + '/api/v0';

export async function exportAsJson(token: string): Promise<Blob> {
	const response = await fetch(`${API_BASE}/export/json`, {
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Export failed' }));
		throw new Error(error.detail || 'Export failed');
	}

	return response.blob();
}

export async function exportAsCsv(token: string): Promise<Blob> {
	const response = await fetch(`${API_BASE}/export/csv`, {
		headers: {
			Authorization: `Bearer ${token}`
		}
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Export failed' }));
		throw new Error(error.detail || 'Export failed');
	}

	return response.blob();
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
