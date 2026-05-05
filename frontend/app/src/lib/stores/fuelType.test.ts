import { test, expect, describe, vi } from 'vitest';
import { get } from 'svelte/store';

const mockLocalStorage = {
	getItem: vi.fn().mockReturnValue(null),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

vi.stubGlobal('localStorage', mockLocalStorage);

vi.stubGlobal('window', {});

vi.mock('$app/environment', () => ({
	browser: true
}));

describe('fuelType store', () => {
	test('initializes with default "diesel" when no stored value', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		expect(get(fuelType)).toBe('diesel');
	});

	test('initializes with stored value "e5" from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue('e5');
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		expect(get(fuelType)).toBe('e5');
	});

	test('initializes with stored value "e10" from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue('e10');
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		expect(get(fuelType)).toBe('e10');
	});

	test('initializes with stored value "diesel" from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue('diesel');
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		expect(get(fuelType)).toBe('diesel');
	});

	test('defaults to "diesel" for invalid stored value', async () => {
		mockLocalStorage.getItem.mockReturnValue('invalid-fuel');
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		expect(get(fuelType)).toBe('diesel');
	});

	test('set updates the store and localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		mockLocalStorage.setItem.mockClear();
		fuelType.set('e5');
		expect(get(fuelType)).toBe('e5');
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('fuelType', 'e5');
	});

	test('set works with all valid fuel types', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		fuelType.set('diesel');
		expect(get(fuelType)).toBe('diesel');
		fuelType.set('e5');
		expect(get(fuelType)).toBe('e5');
		fuelType.set('e10');
		expect(get(fuelType)).toBe('e10');
	});

	test('update modifies the store value', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		fuelType.set('diesel');
		fuelType.update((current) => {
			expect(current).toBe('diesel');
			return 'e10';
		});
		expect(get(fuelType)).toBe('e10');
	});
});
