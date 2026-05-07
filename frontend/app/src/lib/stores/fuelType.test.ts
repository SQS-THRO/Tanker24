import { test, expect, describe, beforeEach, vi } from 'vitest';
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

describe('fuelTypeLabel derived store', () => {
	beforeEach(() => {
		mockLocalStorage.getItem.mockReturnValue(null);
	});

	test('returns "Diesel" when fuelType is "diesel"', async () => {
		vi.doMock('$lib/stores/locale', () => ({
			t: { subscribe: (run: (v: unknown) => void) => { run({ map: { diesel: 'Diesel', e5: 'Super E5', e10: 'Super E10' } }); return () => {}; } }
		}));
		vi.resetModules();
		const { fuelType, fuelTypeLabel } = await import('$lib/stores/fuelType');
		fuelType.set('diesel');
		expect(get(fuelTypeLabel)).toBe('Diesel');
	});

	test('returns "Super E5" when fuelType is "e5"', async () => {
		vi.doMock('$lib/stores/locale', () => ({
			t: { subscribe: (run: (v: unknown) => void) => { run({ map: { diesel: 'Diesel', e5: 'Super E5', e10: 'Super E10' } }); return () => {}; } }
		}));
		vi.resetModules();
		const { fuelType, fuelTypeLabel } = await import('$lib/stores/fuelType');
		fuelType.set('e5');
		expect(get(fuelTypeLabel)).toBe('Super E5');
	});

	test('returns "Super E10" when fuelType is "e10"', async () => {
		vi.doMock('$lib/stores/locale', () => ({
			t: { subscribe: (run: (v: unknown) => void) => { run({ map: { diesel: 'Diesel', e5: 'Super E5', e10: 'Super E10' } }); return () => {}; } }
		}));
		vi.resetModules();
		const { fuelType, fuelTypeLabel } = await import('$lib/stores/fuelType');
		fuelType.set('e10');
		expect(get(fuelTypeLabel)).toBe('Super E10');
	});

	test('updates label reactively when fuelType changes', async () => {
		vi.doMock('$lib/stores/locale', () => ({
			t: { subscribe: (run: (v: unknown) => void) => { run({ map: { diesel: 'Diesel', e5: 'Super E5', e10: 'Super E10' } }); return () => {}; } }
		}));
		vi.resetModules();
		const { fuelType, fuelTypeLabel } = await import('$lib/stores/fuelType');
		fuelType.set('diesel');
		expect(get(fuelTypeLabel)).toBe('Diesel');
		fuelType.set('e10');
		expect(get(fuelTypeLabel)).toBe('Super E10');
	});
});

describe('fuelType store in non-browser environment', () => {
	test('initializes with "diesel" without calling localStorage', async () => {
		vi.doMock('$app/environment', () => ({ browser: false }));
		vi.resetModules();
		mockLocalStorage.getItem.mockClear();
		const { fuelType } = await import('$lib/stores/fuelType');
		expect(get(fuelType)).toBe('diesel');
		expect(mockLocalStorage.getItem).not.toHaveBeenCalledWith('fuelType');
	});

	test('set does not write to localStorage', async () => {
		vi.doMock('$app/environment', () => ({ browser: false }));
		vi.resetModules();
		const { fuelType } = await import('$lib/stores/fuelType');
		mockLocalStorage.setItem.mockClear();
		fuelType.set('e5');
		expect(get(fuelType)).toBe('e5');
		expect(mockLocalStorage.setItem).not.toHaveBeenCalledWith('fuelType');
	});
});
