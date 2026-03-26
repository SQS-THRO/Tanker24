import { request } from '$lib/utils/request';

export interface Station {
	id: number;
	name: string;
	description: string | null;
	latitude: number | null;
	longitude: number | null;
	owner_id: number;
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
