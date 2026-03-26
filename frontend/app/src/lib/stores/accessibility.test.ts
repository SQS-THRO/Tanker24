import { test, expect, describe, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';

const mockLocalStorage = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

vi.stubGlobal('localStorage', mockLocalStorage);
vi.stubGlobal('navigator', { language: 'en' });

vi.mock('$app/environment', () => ({
	browser: true
}));

beforeEach(() => {
	mockLocalStorage.getItem.mockReturnValue(null);
	mockLocalStorage.setItem.mockReset();
	mockLocalStorage.removeItem.mockReset();
	vi.resetModules();
});

describe('colorblindMode store', () => {
	test('initializes with "none" when no stored value', async () => {
		const { colorblindMode } = await import('$lib/stores/accessibility');
		expect(get(colorblindMode)).toBe('none');
	});

	test('initializes with stored value from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue('protanopia');
		vi.resetModules();
		const { colorblindMode } = await import('$lib/stores/accessibility');
		expect(get(colorblindMode)).toBe('protanopia');
	});

	test('initializes with "none" for invalid stored value', async () => {
		mockLocalStorage.getItem.mockReturnValue('invalid-mode');
		vi.resetModules();
		const { colorblindMode } = await import('$lib/stores/accessibility');
		expect(get(colorblindMode)).toBe('none');
	});

	test('set updates the store and localStorage', async () => {
		const { colorblindMode } = await import('$lib/stores/accessibility');
		colorblindMode.set('deuteranopia');
		expect(get(colorblindMode)).toBe('deuteranopia');
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('colorblindMode', 'deuteranopia');
	});

	test('reset sets to "none" and removes from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue('protanopia');
		vi.resetModules();
		const { colorblindMode } = await import('$lib/stores/accessibility');
		colorblindMode.reset();
		expect(get(colorblindMode)).toBe('none');
		expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('colorblindMode');
	});
});

describe('colorblindFilter derived store', () => {
	test('returns null when mode is "none"', async () => {
		const { colorblindFilter } = await import('$lib/stores/accessibility');
		expect(get(colorblindFilter)).toBeNull();
	});

	test('returns mode when mode is not "none"', async () => {
		vi.resetModules();
		const { colorblindMode, colorblindFilter } = await import('$lib/stores/accessibility');
		colorblindMode.set('protanopia');
		expect(get(colorblindFilter)).toBe('protanopia');
	});
});