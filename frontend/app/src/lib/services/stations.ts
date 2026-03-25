import { env } from '$env/dynamic/public';

const API_BASE = env.PUBLIC_BACKEND_URL ?? 'http://localhost:8000';

export interface Station {
	id: number;
	name: string;
	description: string | null;
	latitude: number | null;
	longitude: number | null;
	owner_id: number;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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

export const stationService = {
	async getStations(token: string): Promise<Station[]> {
		return request<Station[]>('/stations/', {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
	},

	async getStation(stationId: number, token: string): Promise<Station> {
		return request<Station>(`/stations/${stationId}`, {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
	},

	async createStation(station: Omit<Station, 'id' | 'owner_id'>, token: string): Promise<Station> {
		return request<Station>('/stations/', {
			method: 'POST',
			body: JSON.stringify(station),
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
	}
};
