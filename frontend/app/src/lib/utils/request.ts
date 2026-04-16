import { env } from '$env/dynamic/public';

const API_BASE = (env.PUBLIC_BACKEND_URL ?? 'http://127.0.0.1:8000') + '/api/v0';

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
	const response = await fetch(`${API_BASE}${endpoint}`, {
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		...options
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Request failed' }));
		throw new Error(error.detail || 'Request failed');
	}

	return response.json();
}
