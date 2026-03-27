import { test, expect, describe, beforeEach, vi, afterEach } from 'vitest';
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

describe('themeStore', () => {
	beforeEach(() => {
		mockLocalStorage.getItem.mockReturnValue(null);
		mockLocalStorage.setItem.mockClear();
	});

	afterEach(() => {
		vi.resetModules();
	});

	test('initializes with default settings when no stored value', async () => {
		const { themeStore } = await import('$lib/stores/theme');
		const settings = get(themeStore);
		expect(settings.globalTheme).toBe('dark-modern');
		expect(settings.colorBlindOverride).toBe('none');
	});

	test('initializes with stored settings from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue(JSON.stringify({ globalTheme: 'dark-modern', colorBlindOverride: 'protanopia' }));
		vi.resetModules();
		const { themeStore } = await import('$lib/stores/theme');
		const settings = get(themeStore);
		expect(settings.colorBlindOverride).toBe('protanopia');
	});

	test('setGlobalTheme updates the store and localStorage', async () => {
		const { themeStore } = await import('$lib/stores/theme');
		themeStore.setGlobalTheme('dark-modern');
		const settings = get(themeStore);
		expect(settings.globalTheme).toBe('dark-modern');
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme-settings', JSON.stringify({ globalTheme: 'dark-modern', colorBlindOverride: 'none' }));
	});

	test('setColorBlindOverride updates the store and localStorage', async () => {
		const { themeStore } = await import('$lib/stores/theme');
		themeStore.setColorBlindOverride('deuteranopia');
		const settings = get(themeStore);
		expect(settings.colorBlindOverride).toBe('deuteranopia');
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme-settings', JSON.stringify({ globalTheme: 'dark-modern', colorBlindOverride: 'deuteranopia' }));
	});

	test('reset restores default settings', async () => {
		const { themeStore } = await import('$lib/stores/theme');
		themeStore.setColorBlindOverride('tritanopia');
		themeStore.reset();
		const settings = get(themeStore);
		expect(settings.globalTheme).toBe('dark-modern');
		expect(settings.colorBlindOverride).toBe('none');
	});

	test('preserves other settings when updating one', async () => {
		const { themeStore } = await import('$lib/stores/theme');
		themeStore.setColorBlindOverride('protanopia');
		themeStore.setGlobalTheme('dark-modern');
		const settings = get(themeStore);
		expect(settings.globalTheme).toBe('dark-modern');
		expect(settings.colorBlindOverride).toBe('protanopia');
	});
});

describe('CVD_PALETTES', () => {
	test('none returns null', async () => {
		const { CVD_PALETTES } = await import('$lib/stores/theme');
		expect(CVD_PALETTES.none).toBeNull();
	});

	test('protanopia returns a palette', async () => {
		const { CVD_PALETTES } = await import('$lib/stores/theme');
		expect(CVD_PALETTES.protanopia).toEqual(
			expect.objectContaining({
				bgPrimary: '#0a0a0b',
				accentPrimary: '#e67e22'
			})
		);
	});

	test('deuteranopia returns a palette', async () => {
		const { CVD_PALETTES } = await import('$lib/stores/theme');
		expect(CVD_PALETTES.deuteranopia).toEqual(
			expect.objectContaining({
				bgPrimary: '#0a0a0b',
				accentPrimary: '#9b59b6'
			})
		);
	});

	test('tritanopia returns a palette', async () => {
		const { CVD_PALETTES } = await import('$lib/stores/theme');
		expect(CVD_PALETTES.tritanopia).toEqual(
			expect.objectContaining({
				bgPrimary: '#0a0a0b',
				accentPrimary: '#e91e63'
			})
		);
	});
});

describe('GLOBAL_THEMES', () => {
	test('contains dark-modern theme', async () => {
		const { GLOBAL_THEMES } = await import('$lib/stores/theme');
		expect(GLOBAL_THEMES).toContainEqual({ id: 'dark-modern', name: 'Dark Modern' });
	});
});

describe('COLOR_BLIND_OPTIONS', () => {
	test('contains all color blind options', async () => {
		const { COLOR_BLIND_OPTIONS } = await import('$lib/stores/theme');
		expect(COLOR_BLIND_OPTIONS).toContainEqual({
			id: 'none',
			name: 'None',
			description: 'Default colors'
		});
		expect(COLOR_BLIND_OPTIONS).toContainEqual({
			id: 'protanopia',
			name: 'Protanopia',
			description: 'Red-blind (most common)'
		});
		expect(COLOR_BLIND_OPTIONS).toContainEqual({
			id: 'deuteranopia',
			name: 'Deuteranopia',
			description: 'Green-blind'
		});
		expect(COLOR_BLIND_OPTIONS).toContainEqual({
			id: 'tritanopia',
			name: 'Tritanopia',
			description: 'Blue-blind (rare)'
		});
	});
});
