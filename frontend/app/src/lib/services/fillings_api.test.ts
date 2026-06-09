import { test, expect, beforeEach, vi } from 'vitest';

const fillingRecordFixture = {
	id: 1,
	license_plate_number: 'RO-AB-123',
	car_type: 'VW Golf',
	mileage: 450,
	timestamp: '2024-06-01T12:00:00Z',
	price_per_litre: 1.859,
	litres: 45.5,
	tankerkoenig_station_id: 'tk-001',
	fuel_type: 'e5'
};

const fillingsListFixture = [
	fillingRecordFixture,
	{
		id: 2,
		license_plate_number: 'RO-CD-456',
		car_type: 'BMW 3er',
		mileage: 320,
		timestamp: '2024-06-15T08:30:00Z',
		price_per_litre: 1.729,
		litres: 38.2,
		tankerkoenig_station_id: 'tk-002',
		fuel_type: 'diesel'
	}
];

const createPayloadFixture = {
	license_plate_number: 'RO-AB-123',
	car_type: 'VW Golf',
	mileage: 450,
	timestamp: '2024-06-01T12:00:00Z',
	price_per_litre: 1.859,
	litres: 45.5,
	tankerkoenig_station_id: 'tk-001',
	fuel_type: 'e5' as const
};

const successMessageFixture = { message: 'Filling created successfully' };
const deleteMessageFixture = { message: 'Filling deleted successfully' };

const mockFetch = vi.fn();

vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

test('getFillings sends correct request with auth header', async () => {
	const { getFillings } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(fillingsListFixture)
	});

	const result = await getFillings('test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/fillings'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toEqual(fillingsListFixture);
});

test('getFillings returns empty array when no fillings', async () => {
	const { getFillings } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve([])
	});

	const result = await getFillings('test-token');

	expect(result).toEqual([]);
});

test('getFillings throws error on failure', async () => {
	const { getFillings } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Unauthorized' })
	});

	await expect(getFillings('invalid-token')).rejects.toThrow('Unauthorized');
});

test('getFillings handles malformed error JSON', async () => {
	const { getFillings } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(getFillings('test-token')).rejects.toThrow('Failed to load fillings');
});

test('createFilling sends correct POST request with auth header and body', async () => {
	const { createFilling } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(successMessageFixture)
	});

	const result = await createFilling('test-token-12345', createPayloadFixture);

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/fillings/create'),
		expect.objectContaining({
			method: 'POST',
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			}),
			body: JSON.stringify(createPayloadFixture)
		})
	);
	expect(result).toEqual(successMessageFixture);
});

test('createFilling throws error on failure', async () => {
	const { createFilling } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Invalid fuel type' })
	});

	await expect(createFilling('test-token', createPayloadFixture)).rejects.toThrow('Invalid fuel type');
});

test('createFilling throws fallback error on malformed response', async () => {
	const { createFilling } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(createFilling('test-token', createPayloadFixture)).rejects.toThrow('Failed to save filling');
});

test('deleteFilling sends correct DELETE request with auth header and query param', async () => {
	const { deleteFilling } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(deleteMessageFixture)
	});

	const result = await deleteFilling('test-token-12345', 42);

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/fillings/delete?filling_id=42'),
		expect.objectContaining({
			method: 'DELETE',
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toEqual(deleteMessageFixture);
});

test('deleteFilling throws error on failure', async () => {
	const { deleteFilling } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Filling not found' })
	});

	await expect(deleteFilling('test-token', 999)).rejects.toThrow('Filling not found');
});

test('deleteFilling throws fallback error on malformed response', async () => {
	const { deleteFilling } = await import('./fillings_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(deleteFilling('test-token', 1)).rejects.toThrow('Failed to delete filling');
});
