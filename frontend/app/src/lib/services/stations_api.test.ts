import { test, expect, beforeEach, vi } from 'vitest';

const stationFixture = {
	id: 1,
	name: 'Station A',
	description: 'A test station',
	latitude: 48.1372,
	longitude: 11.5755,
	owner_id: 1
};

const stationListFixture = [
	{
		id: 1,
		name: 'Station A',
		description: 'A test station',
		latitude: 48.1372,
		longitude: 11.5755,
		owner_id: 1
	},
	{
		id: 2,
		name: 'Station B',
		description: null,
		latitude: 52.52,
		longitude: 13.405,
		owner_id: 1
	}
];

const createStationFixture = {
	name: 'New Station',
	description: 'A new test station',
	latitude: 48.1372,
	longitude: 11.5755
};

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
	e10: 1.70,
	is_open: true,
	cached_at: '2024-01-01T12:00:00Z',
	cache_lat: 52.52,
	cache_lon: 13.405,
	cache_radius: 5.0
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
		distance: 1.0,
		diesel: 1.66,
		e5: 1.76,
		e10: 1.71,
		is_open: false,
		cached_at: '2024-01-01T12:00:00Z',
		cache_lat: 52.52,
		cache_lon: 13.405,
		cache_radius: 5.0
	}
];

const mockFetch = vi.fn();

vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

test('getStations sends correct request with auth header', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(stationListFixture)
	});

	const result = await stationService.getStations('test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/stations/'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toEqual(stationListFixture);
});

test('getStations returns empty array when no stations', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve([])
	});

	const result = await stationService.getStations('test-token');

	expect(result).toEqual([]);
});

test('getStations throws error on failure', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Unauthorized' })
	});

	await expect(stationService.getStations('invalid-token')).rejects.toThrow('Unauthorized');
});

test('getStation sends correct request with id and auth header', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(stationFixture)
	});

	const result = await stationService.getStation(1, 'test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/stations/1'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toEqual(stationFixture);
});

test('getStation throws error on failure', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Station not found' })
	});

	await expect(stationService.getStation(99999, 'test-token')).rejects.toThrow('Station not found');
});

test('getStation handles malformed error JSON', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(stationService.getStation(1, 'test-token')).rejects.toThrow('Request failed');
});

test('createStation sends correct data to API', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve({ ...createStationFixture, id: 3, owner_id: 1 })
	});

	const result = await stationService.createStation(createStationFixture, 'test-token-12345');

	const call = mockFetch.mock.calls[0];
	expect(call[0]).toContain('/stations/');
	expect(call[1].method).toBe('POST');
	expect(call[1].headers['Authorization']).toBe('Bearer test-token-12345');
	expect(call[1].body).toBe(JSON.stringify(createStationFixture));
	expect(result).toEqual({ ...createStationFixture, id: 3, owner_id: 1 });
});

test('createStation throws error on failure', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Validation error' })
	});

	await expect(stationService.createStation(createStationFixture, 'test-token')).rejects.toThrow('Validation error');
});

test('createStation parses generic error when JSON has no detail', async () => {
	const { stationService } = await import('./stations_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ message: 'Server error' })
	});

	await expect(stationService.createStation(createStationFixture, 'test-token')).rejects.toThrow('Request failed');
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
