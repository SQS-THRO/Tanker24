import { writable } from 'svelte/store';

const STORAGE_KEY = 'privacy-settings';

const DEFAULT_SETTINGS = {
	analyticsAccepted: false,
	hidden: false
};

function loadSettings() {
	if (globalThis.window === undefined) return DEFAULT_SETTINGS;

	const stored = localStorage.getItem(STORAGE_KEY);
	if (!stored) return DEFAULT_SETTINGS;

	try {
		const parsed = JSON.parse(stored);
		return { ...DEFAULT_SETTINGS, ...parsed, hidden: false };
	} catch {
		return DEFAULT_SETTINGS;
	}
}

function saveSettings(settings: typeof DEFAULT_SETTINGS) {
	if (globalThis.window === undefined) return;
	localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

function createPrivacyStore() {
	const initial = loadSettings();
	const { subscribe, set, update } = writable(initial);

	return {
		subscribe,
		acceptAnalytics: () => {
			update((s) => {
				const newSettings = { ...s, analyticsAccepted: true };
				saveSettings(newSettings);
				return newSettings;
			});
		},
		declineAnalytics: () => {
			update((s) => {
				const newSettings = { ...s, analyticsAccepted: false, hidden: true };
				saveSettings(newSettings);
				return newSettings;
			});
		},
		reset: () => {
			set(DEFAULT_SETTINGS);
			saveSettings(DEFAULT_SETTINGS);
		}
	};
}

export const privacyStore = createPrivacyStore();
