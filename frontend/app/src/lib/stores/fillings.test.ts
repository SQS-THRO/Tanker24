import { test, expect, describe, afterEach, vi } from 'vitest';
import { get } from 'svelte/store';

const mockToken = 'mock-jwt-token';

const mockFillingRecord = {
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

const mockFillingRecord2 = {
	id: 2,
	license_plate_number: 'RO-CD-456',
	car_type: 'BMW 3er',
	mileage: 320,
	timestamp: '2024-06-15T08:30:00Z',
	price_per_litre: 1.729,
	litres: 38.2,
	tankerkoenig_station_id: 'tk-002',
	fuel_type: 'diesel'
};

const mockCreatePayload = {
	license_plate_number: 'RO-AB-123',
	car_type: 'VW Golf',
	mileage: 450,
	timestamp: '2024-06-01T12:00:00Z',
	price_per_litre: 1.859,
	litres: 45.5,
	tankerkoenig_station_id: 'tk-001',
	fuel_type: 'e5' as const
};

const mockFillingsApi = {
	getFillings: vi.fn(),
	createFilling: vi.fn(),
	deleteFilling: vi.fn()
};

vi.mock('$lib/services/fillings_api', () => mockFillingsApi);

vi.mock('$app/environment', () => ({ browser: true }));

afterEach(() => {
	vi.resetModules();
});

describe('fillings store', () => {
	test('initializes with empty data', async () => {
		const { fillings } = await import('$lib/stores/fillings');
		const state = get(fillings);
		expect(state.data).toEqual([]);
		expect(state.loading).toBe(false);
		expect(state.error).toBeNull();
	});

	test('fetchFillings sets loading and populates data on success', async () => {
		mockFillingsApi.getFillings.mockResolvedValue([mockFillingRecord, mockFillingRecord2]);
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.fetchFillings(mockToken);
		const state = get(fillings);
		expect(state.loading).toBe(false);
		expect(state.error).toBeNull();
		expect(state.data).toEqual([mockFillingRecord, mockFillingRecord2]);
		expect(mockFillingsApi.getFillings).toHaveBeenCalledWith(mockToken);
	});

	test('fetchFillings sets error on failure', async () => {
		mockFillingsApi.getFillings.mockRejectedValue(new Error('Failed to load fillings'));
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.fetchFillings(mockToken);
		const state = get(fillings);
		expect(state.loading).toBe(false);
		expect(state.error).toBe('Failed to load fillings');
		expect(state.data).toEqual([]);
	});

	test('fetchFillings sets generic error when exception has no message', async () => {
		mockFillingsApi.getFillings.mockRejectedValue({});
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.fetchFillings(mockToken);
		const state = get(fillings);
		expect(state.loading).toBe(false);
		expect(state.error).toBe('Failed to load fillings');
	});

	test('removeFilling calls API and removes record from data', async () => {
		mockFillingsApi.getFillings.mockResolvedValue([mockFillingRecord, mockFillingRecord2]);
		mockFillingsApi.deleteFilling.mockResolvedValue({ message: 'Filling deleted successfully' });
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.fetchFillings(mockToken);
		expect(get(fillings).data).toHaveLength(2);
		await fillings.removeFilling(mockToken, 1);
		const state = get(fillings);
		expect(state.data).toEqual([mockFillingRecord2]);
		expect(mockFillingsApi.deleteFilling).toHaveBeenCalledWith(mockToken, 1);
	});

	test('removeFilling throws on API failure', async () => {
		mockFillingsApi.getFillings.mockResolvedValue([mockFillingRecord]);
		mockFillingsApi.deleteFilling.mockRejectedValue(new Error('Filling not found'));
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.fetchFillings(mockToken);
		await expect(fillings.removeFilling(mockToken, 999)).rejects.toThrow('Filling not found');
	});

	test('removeFilling preserves data on API failure', async () => {
		mockFillingsApi.getFillings.mockResolvedValue([mockFillingRecord, mockFillingRecord2]);
		mockFillingsApi.deleteFilling.mockRejectedValue(new Error('Filling not found'));
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.fetchFillings(mockToken);
		await expect(fillings.removeFilling(mockToken, 999)).rejects.toThrow('Filling not found');
		const state = get(fillings);
		expect(state.data).toHaveLength(2);
	});

	test('createFilling calls API with payload', async () => {
		mockFillingsApi.createFilling.mockResolvedValue({ message: 'Filling created successfully' });
		const { fillings } = await import('$lib/stores/fillings');
		await fillings.createFilling(mockToken, mockCreatePayload);
		expect(mockFillingsApi.createFilling).toHaveBeenCalledWith(mockToken, mockCreatePayload);
	});

	test('createFilling propagates API error', async () => {
		mockFillingsApi.createFilling.mockRejectedValue(new Error('Invalid fuel type'));
		const { fillings } = await import('$lib/stores/fillings');
		await expect(fillings.createFilling(mockToken, mockCreatePayload)).rejects.toThrow('Invalid fuel type');
	});
});
