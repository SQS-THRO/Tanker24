import { test, expect, beforeEach, vi } from 'vitest';

const tankerkoenigStationFixture = {
	id: 1,
	tankerkoenig_id: 'tk-001',
	name: 'Shell Station',
	brand: 'Shell',
	street: 'Main Street',
	house_number: '42',
	post_code: 10115,
	place: 'Berlin',
	latitude: 52.52,
	longitude: 13.405,
	distance: 0.5,
	diesel: 1.65,
	e5: 1.75,
	e10: 1.7,
	is_open: true,
	cached_at: '2024-01-01T12:00:00Z',
	cache_lat: 52.52,
	cache_lon: 13.405,
	cache_radius: 5.1
};

const nearbyStationsListFixture = [
	tankerkoenigStationFixture,
	{
		id: 2,
		tankerkoenig_id: 'tk-002',
		name: 'Aral Station',
		brand: 'Aral',
		street: 'Second Street',
		house_number: '10',
		post_code: 10117,
		place: 'Berlin',
		latitude: 52.53,
		longitude: 13.406,
		distance: 1.1,
		diesel: 1.66,
		e5: 1.76,
		e10: 1.71,
		is_open: false,
		cached_at: '2024-01-01T12:00:00Z',
		cache_lat: 52.52,
		cache_lon: 13.405,
		cache_radius: 5.1
	}
];

const mockFetch = vi.fn();

vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

test('getNearbyStations sends correct request with auth header and query params', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(nearbyStationsListFixture)
	});

	const result = await stationService.getNearbyStations(52.52, 13.405, 'test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/stations/nearby?latitude=52.52&longitude=13.405'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toEqual(nearbyStationsListFixture);
});

test('getNearbyStations returns empty array when no stations found', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve([])
	});

	const result = await stationService.getNearbyStations(48.1, 11.5, 'test-token');

	expect(result).toEqual([]);
});

test('getNearbyStations throws error on failure', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Rate limit exceeded' })
	});

	await expect(stationService.getNearbyStations(48.1, 11.5, 'test-token')).rejects.toThrow('Rate limit exceeded');
});

test('getNearbyStations handles malformed error JSON', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(stationService.getNearbyStations(52.52, 13.405, 'test-token')).rejects.toThrow('Request failed');
});
