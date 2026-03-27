import { writable } from 'svelte/store';

export type ColorBlindOverride = 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia';
export type GlobalTheme = 'dark-modern';

export interface ThemePalette {
	bgPrimary: string;
	bgSecondary: string;
	bgCard: string;
	bgCardHover: string;
	bgElevated: string;
	textPrimary: string;
	textSecondary: string;
	textMuted: string;
	accentPrimary: string;
	accentSecondary: string;
	accentGradient: string;
	success: string;
	error: string;
	warning: string;
}

const STORAGE_KEY = 'theme-settings';

const DEFAULT_SETTINGS = {
	globalTheme: 'dark-modern' as GlobalTheme,
	colorBlindOverride: 'none' as ColorBlindOverride
};

function loadSettings() {
	if (globalThis.window === undefined) return DEFAULT_SETTINGS;

	const stored = localStorage.getItem(STORAGE_KEY);
	if (!stored) return DEFAULT_SETTINGS;

	try {
		return JSON.parse(stored);
	} catch {
		return DEFAULT_SETTINGS;
	}
}

function saveSettings(settings: typeof DEFAULT_SETTINGS) {
	if (globalThis.window === undefined) return;
	localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

function createThemeStore() {
	const initial = loadSettings();
	const { subscribe, set, update } = writable(initial);

	return {
		subscribe,
		setGlobalTheme: (theme: GlobalTheme) => {
			update((s) => {
				const newSettings = { ...s, globalTheme: theme };
				saveSettings(newSettings);
				return newSettings;
			});
		},
		setColorBlindOverride: (override: ColorBlindOverride) => {
			update((s) => {
				const newSettings = { ...s, colorBlindOverride: override };
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

export const themeStore = createThemeStore();

export const CVD_PALETTES: Record<ColorBlindOverride, ThemePalette | null> = {
	none: null,
	protanopia: {
		bgPrimary: '#0a0a0b',
		bgSecondary: '#141416',
		bgCard: '#1a1a1d',
		bgCardHover: '#222225',
		bgElevated: '#2a2a2e',
		textPrimary: '#ffffff',
		textSecondary: '#a1a1aa',
		textMuted: '#71717a',
		accentPrimary: '#e67e22',
		accentSecondary: '#f39c12',
		accentGradient: 'linear-gradient(135deg, #e67e22 0%, #f39c12 50%, #f1c40f 100%)',
		success: '#27ae60',
		error: '#c0392b',
		warning: '#f39c12'
	},
	deuteranopia: {
		bgPrimary: '#0a0a0b',
		bgSecondary: '#141416',
		bgCard: '#1a1a1d',
		bgCardHover: '#222225',
		bgElevated: '#2a2a2e',
		textPrimary: '#ffffff',
		textSecondary: '#a1a1aa',
		textMuted: '#71717a',
		accentPrimary: '#9b59b6',
		accentSecondary: '#8e44ad',
		accentGradient: 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 50%, #7d3c98 100%)',
		success: '#27ae60',
		error: '#c0392b',
		warning: '#f39c12'
	},
	tritanopia: {
		bgPrimary: '#0a0a0b',
		bgSecondary: '#141416',
		bgCard: '#1a1a1d',
		bgCardHover: '#222225',
		bgElevated: '#2a2a2e',
		textPrimary: '#ffffff',
		textSecondary: '#a1a1aa',
		textMuted: '#71717a',
		accentPrimary: '#e91e63',
		accentSecondary: '#ff6384',
		accentGradient: 'linear-gradient(135deg, #e91e63 0%, #ff6384 50%, #ff4081 100%)',
		success: '#2ecc71',
		error: '#e74c3c',
		warning: '#f1c40f'
	}
};

export const GLOBAL_THEMES: { id: GlobalTheme; name: string }[] = [{ id: 'dark-modern', name: 'Dark Modern' }];

export const COLOR_BLIND_OPTIONS: { id: ColorBlindOverride; name: string; description: string }[] = [
	{ id: 'none', name: 'None', description: 'Default colors' },
	{ id: 'protanopia', name: 'Protanopia', description: 'Red-blind (most common)' },
	{ id: 'deuteranopia', name: 'Deuteranopia', description: 'Green-blind' },
	{ id: 'tritanopia', name: 'Tritanopia', description: 'Blue-blind (rare)' }
];
