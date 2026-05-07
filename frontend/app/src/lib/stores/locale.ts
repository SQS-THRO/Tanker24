import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { translations, type Locale, type TranslationKeys } from '$lib/i18n/index';

export function detectLocale(): Locale {
	if (!browser) return 'en';

	const stored = localStorage.getItem('locale');
	if (stored === 'en' || stored === 'de') {
		return stored;
	}

	const navLang = navigator.language || navigator.languages?.[0] || '';
	if (navLang.toLowerCase().startsWith('de')) {
		return 'de';
	}

	return 'en';
}

function createLocaleStore() {
	const { subscribe, set, update } = writable<Locale>(browser ? detectLocale() : 'en');

	return {
		subscribe,
		set: (locale: Locale) => {
			if (browser) {
				localStorage.setItem('locale', locale);
			}
			set(locale);
		},
		toggle: () => {
			update((current) => {
				const newLocale = current === 'en' ? 'de' : 'en';
				if (browser) {
					localStorage.setItem('locale', newLocale);
				}
				return newLocale;
			});
		}
	};
}

export const locale = createLocaleStore();

export const t = derived(locale, ($locale) => {
	return translations[$locale];
});

export function getTranslation(obj: TranslationKeys, path: string): string {
	const keys = path.split('.');
	let result: TranslationKeys | string = obj;
	for (const key of keys) {
		if (result && typeof result === 'object' && key in result) {
			result = result[key];
		} else {
			return path;
		}
	}
	return typeof result === 'string' ? result : path;
}
