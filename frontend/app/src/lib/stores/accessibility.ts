import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

export type ColorBlindMode = 'none' | 'protanopia' | 'protanomaly' | 'deuteranopia' | 'deuteranomaly' | 'tritanopia' | 'tritanomaly' | 'achromatopsia' | 'achromatomaly';

const COLORBLIND_MODES: Set<ColorBlindMode> = new Set([
	'none',
	'protanopia',
	'protanomaly',
	'deuteranopia',
	'deuteranomaly',
	'tritanopia',
	'tritanomaly',
	'achromatopsia',
	'achromatomaly'
]);

function createAccessibilityStore() {
	const stored = browser ? localStorage.getItem('colorblindMode') : null;
	const initial: ColorBlindMode = stored && COLORBLIND_MODES.has(stored as ColorBlindMode) ? (stored as ColorBlindMode) : 'none';

	const { subscribe, set } = writable<ColorBlindMode>(initial);

	return {
		subscribe,
		set: (mode: ColorBlindMode) => {
			if (browser) {
				localStorage.setItem('colorblindMode', mode);
			}
			set(mode);
		},
		reset: () => {
			if (browser) {
				localStorage.removeItem('colorblindMode');
			}
			set('none');
		}
	};
}

export const colorblindMode = createAccessibilityStore();

export const colorblindFilter = derived(colorblindMode, ($mode) => {
	if ($mode === 'none') return null;
	return $mode;
});
