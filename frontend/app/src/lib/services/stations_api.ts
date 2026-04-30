import { request } from '$lib/utils/request';

export interface Station {
	id: number;
	name: string;
	description: string | null;
	latitude: number | null;
	longitude: number | null;
	owner_id: number;
}

export interface TankerkoenigStation {
	id: number;
	tankerkoenig_id: string;
	name: string;
	brand: string;
	street: string | null;
	house_number: string | null;
	post_code: number | null;
	place: string | null;
	latitude: number;
	longitude: number;
	distance: number | null;
	diesel: number | null;
	e5: number | null;
	e10: number | null;
	is_open: boolean;
	cached_at: string;
	cache_lat: number | null;
	cache_lon: number | null;
	cache_radius: number | null;
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
	},

	async getNearbyStations(latitude: number, longitude: number, token: string): Promise<TankerkoenigStation[]> {
		return request<TankerkoenigStation[]>(`/stations/nearby?latitude=${latitude}&longitude=${longitude}`, {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
	}
};
