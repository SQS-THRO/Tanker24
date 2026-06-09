import { env } from '$env/dynamic/public';

const API_BASE = (env.PUBLIC_BACKEND_URL ?? 'http://127.0.0.1:8000') + '/api/v0';

export { API_BASE };

interface RequestOptions extends RequestInit {
	responseType?: 'json' | 'blob' | 'text';
	fallbackError?: string;
}

export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
	const { responseType = 'json', fallbackError = 'Request failed', headers: customHeaders, ...fetchOptions } = options;

	const response = await fetch(`${API_BASE}${endpoint}`, {
		...fetchOptions,
		headers: {
			'Content-Type': 'application/json',
			...customHeaders
		}
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: fallbackError }));
		throw new Error(error.detail || fallbackError);
	}

	if (response.status === 204) return undefined as T;

	if (responseType === 'blob') return response.blob() as Promise<T>;
	if (responseType === 'text') return response.text() as Promise<T>;
	return response.json();
}
