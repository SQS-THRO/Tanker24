import { request } from '$lib/utils/request';

export interface FillingRecord {
	id: number | null;
	license_plate_number: string;
	car_type: string;
	mileage: number;
	timestamp: string;
	price_per_litre: number;
	litres: number;
	tankerkoenig_station_id: string;
	fuel_type: 'diesel' | 'e5' | 'e10' | 'all';
}

export async function getFillings(token: string): Promise<FillingRecord[]> {
	return request<FillingRecord[]>('/fillings', {
		headers: {
			Authorization: `Bearer ${token}`
		},
		fallbackError: 'Failed to load fillings'
	});
}

export interface CreateFillingPayload {
	license_plate_number: string;
	car_type: string;
	mileage: number;
	timestamp: string;
	price_per_litre: number;
	litres: number;
	tankerkoenig_station_id: string;
	fuel_type: 'diesel' | 'e5' | 'e10';
}

export async function createFilling(token: string, data: CreateFillingPayload): Promise<{ message: string }> {
	return request<{ message: string }>('/fillings/create', {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(data),
		fallbackError: 'Failed to save filling'
	});
}

export async function deleteFilling(token: string, fillingId: number): Promise<{ message: string }> {
	return request<{ message: string }>(`/fillings/delete?filling_id=${fillingId}`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${token}`
		},
		fallbackError: 'Failed to delete filling'
	});
}
