import { test, expect, describe, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';

const mockLocalStorage = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

vi.stubGlobal('localStorage', mockLocalStorage);

const mockNavigator = { language: 'en', languages: ['en'] };
vi.stubGlobal('navigator', mockNavigator);

vi.mock('$app/environment', () => ({
	browser: true
}));

beforeEach(() => {
	mockLocalStorage.getItem.mockReturnValue(null);
	mockLocalStorage.setItem.mockReset();
	mockLocalStorage.removeItem.mockReset();
	mockNavigator.language = 'en';
	vi.resetModules();
});

describe('locale store', () => {
	test('initializes with "en" when no stored value and no navigator language', async () => {
		mockNavigator.language = 'fr';
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('en');
	});

	test('initializes with stored locale from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue('de');
		vi.resetModules();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('de');
	});

	test('initializes with "de" when navigator.language starts with "de"', async () => {
		mockNavigator.language = 'de-DE';
		vi.resetModules();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('de');
	});

	test('set updates the store and localStorage', async () => {
		const { locale } = await import('$lib/stores/locale');
		locale.set('de');
		expect(get(locale)).toBe('de');
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('locale', 'de');
	});

	test('toggle switches between en and de', async () => {
		const { locale } = await import('$lib/stores/locale');
		locale.set('en');
		locale.toggle();
		expect(get(locale)).toBe('de');
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('locale', 'de');
		locale.toggle();
		expect(get(locale)).toBe('en');
	});
});

describe('t derived store', () => {
	test('returns en translations when locale is "en"', async () => {
		const { t } = await import('$lib/stores/locale');
		const translations = get(t);
		expect(translations.nav.map).toBe('Map');
	});

	test('returns de translations when locale is "de"', async () => {
		vi.resetModules();
		const { locale, t } = await import('$lib/stores/locale');
		locale.set('de');
		const translations = get(t);
		expect(translations.nav.map).toBe('Karte');
	});
});

describe('getTranslation function', () => {
	test('returns translation for valid path', async () => {
		const { getTranslation } = await import('$lib/stores/locale');
		const { translations } = await import('$lib/i18n/index');
		const result = getTranslation(translations.en, 'nav.map');
		expect(result).toBe('Map');
	});

	test('returns path for invalid path', async () => {
		const { getTranslation } = await import('$lib/stores/locale');
		const { translations } = await import('$lib/i18n/index');
		const result = getTranslation(translations.en, 'invalid.path');
		expect(result).toBe('invalid.path');
	});

	test('returns path for partial invalid path', async () => {
		const { getTranslation } = await import('$lib/stores/locale');
		const { translations } = await import('$lib/i18n/index');
		const result = getTranslation(translations.en, 'nav.invalidKey');
		expect(result).toBe('nav.invalidKey');
	});

	test('returns translation for nested path', async () => {
		const { getTranslation } = await import('$lib/stores/locale');
		const { translations } = await import('$lib/i18n/index');
		const result = getTranslation(translations.en, 'hero.badge');
		expect(result).toBe('Save money on fuel');
	});
});
