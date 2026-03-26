import { test, expect, describe } from 'vitest';
import { translations, type Locale, type TranslationKeys } from '$lib/i18n/index';

describe('translations', () => {
	test('exports translations object with en and de locales', () => {
		expect(translations).toHaveProperty('en');
		expect(translations).toHaveProperty('de');
	});

	test('en locale has all required keys', () => {
		const en = translations.en;
		expect(en).toHaveProperty('nav');
		expect(en).toHaveProperty('hero');
		expect(en).toHaveProperty('features');
		expect(en).toHaveProperty('cta');
		expect(en).toHaveProperty('footer');
		expect(en).toHaveProperty('login');
		expect(en).toHaveProperty('register');
		expect(en).toHaveProperty('account');
		expect(en).toHaveProperty('map');
	});

	test('de locale has all required keys', () => {
		const de = translations.de;
		expect(de).toHaveProperty('nav');
		expect(de).toHaveProperty('hero');
		expect(de).toHaveProperty('features');
		expect(de).toHaveProperty('cta');
		expect(de).toHaveProperty('footer');
		expect(de).toHaveProperty('login');
		expect(de).toHaveProperty('register');
		expect(de).toHaveProperty('account');
		expect(de).toHaveProperty('map');
	});

	test('nav translations have required fields for en', () => {
		expect(translations.en.nav).toHaveProperty('map');
		expect(translations.en.nav).toHaveProperty('account');
		expect(translations.en.nav).toHaveProperty('logout');
		expect(translations.en.nav).toHaveProperty('signIn');
		expect(translations.en.nav).toHaveProperty('getStarted');
	});

	test('nav translations have required fields for de', () => {
		expect(translations.de.nav).toHaveProperty('map');
		expect(translations.de.nav).toHaveProperty('account');
		expect(translations.de.nav).toHaveProperty('logout');
		expect(translations.de.nav).toHaveProperty('signIn');
		expect(translations.de.nav).toHaveProperty('getStarted');
	});

	test('account.colorBlindnessModes has all color blind modes', () => {
		const modes = translations.en.account.colorBlindnessModes;
		expect(modes).toHaveProperty('none');
		expect(modes).toHaveProperty('protanopia');
		expect(modes).toHaveProperty('protanomaly');
		expect(modes).toHaveProperty('deuteranopia');
		expect(modes).toHaveProperty('deuteranomaly');
		expect(modes).toHaveProperty('tritanopia');
		expect(modes).toHaveProperty('tritanomaly');
		expect(modes).toHaveProperty('achromatopsia');
		expect(modes).toHaveProperty('achromatomaly');
	});

	test('Locale type is correct', () => {
		const locale: Locale = 'en';
		expect(locale).toBe('en');
	});

	test('TranslationKeys type matches translations structure', () => {
		const keys: TranslationKeys = translations.en;
		expect(keys.nav.map).toBe('Map');
	});
});

describe('translation values', () => {
	test('en and de translations are different', () => {
		expect(translations.en.nav.map).not.toBe(translations.de.nav.map);
	});

	test('en nav.map is "Map"', () => {
		expect(translations.en.nav.map).toBe('Map');
	});

	test('de nav.map is "Karte"', () => {
		expect(translations.de.nav.map).toBe('Karte');
	});
});