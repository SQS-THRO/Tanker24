import { test, expect, describe, beforeEach, afterEach, vi } from 'vitest';
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

const mockEnv = { browser: true };

vi.mock('$app/environment', () => mockEnv);

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

	test('initializes with "en" for invalid stored value', async () => {
		mockLocalStorage.getItem.mockReturnValue('fr');
		vi.resetModules();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('en');
	});

	test('toggle persists to localStorage on each switch', async () => {
		const { locale } = await import('$lib/stores/locale');
		mockLocalStorage.setItem.mockClear();
		locale.toggle();
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('locale', 'de');
		locale.toggle();
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('locale', 'en');
	});
});

describe('detectLocale in non-browser environment', () => {
	beforeEach(() => {
		mockEnv.browser = false;
		vi.resetModules();
	});

	afterEach(() => {
		mockEnv.browser = true;
	});

	test('returns "en" without calling localStorage', async () => {
		mockLocalStorage.getItem.mockClear();
		const { detectLocale } = await import('$lib/stores/locale');
		expect(detectLocale()).toBe('en');
		expect(mockLocalStorage.getItem).not.toHaveBeenCalled();
	});
});

describe('detectLocale navigator fallback', () => {
	test('falls back to navigator.languages[0] when navigator.language is empty', async () => {
		mockNavigator.language = '';
		mockNavigator.languages = ['de-DE'];
		vi.resetModules();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('de');
	});

	test('returns "en" when navigator.language and navigator.languages are empty', async () => {
		mockNavigator.language = '';
		mockNavigator.languages = [];
		vi.resetModules();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('en');
	});

	test('returns "en" when navigator.language is undefined and navigator.languages is empty', async () => {
		mockNavigator.language = undefined as unknown as string;
		mockNavigator.languages = [];
		vi.resetModules();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('en');
	});
});

describe('locale store in non-browser environment', () => {
	beforeEach(() => {
		mockEnv.browser = false;
		vi.resetModules();
	});

	afterEach(() => {
		mockEnv.browser = true;
	});

	test('initializes with "en" without calling localStorage', async () => {
		mockLocalStorage.getItem.mockClear();
		const { locale } = await import('$lib/stores/locale');
		expect(get(locale)).toBe('en');
		expect(mockLocalStorage.getItem).not.toHaveBeenCalled();
	});

	test('set does not write to localStorage', async () => {
		const { locale } = await import('$lib/stores/locale');
		mockLocalStorage.setItem.mockClear();
		locale.set('de');
		expect(get(locale)).toBe('de');
		expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
	});

	test('toggle does not write to localStorage', async () => {
		const { locale } = await import('$lib/stores/locale');
		mockLocalStorage.setItem.mockClear();
		locale.toggle();
		expect(get(locale)).toBe('de');
		expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
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

	test('t updates reactively when locale changes', async () => {
		const { locale, t } = await import('$lib/stores/locale');
		locale.set('en');
		expect(get(t).nav.map).toBe('Map');
		locale.set('de');
		expect(get(t).nav.map).toBe('Karte');
		locale.set('en');
		expect(get(t).nav.map).toBe('Map');
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

	test('returns path when result is an object instead of string', async () => {
		const { getTranslation } = await import('$lib/stores/locale');
		const { translations } = await import('$lib/i18n/index');
		const result = getTranslation(translations.en, 'nav');
		expect(result).toBe('nav');
	});
});
