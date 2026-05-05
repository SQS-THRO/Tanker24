import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { t } from '$lib/stores/locale';

export type FuelType = 'diesel' | 'e5' | 'e10';

const STORAGE_KEY = 'fuelType';

function getInitial(): FuelType {
	if (!browser) return 'diesel';
	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored === 'diesel' || stored === 'e5' || stored === 'e10') {
		return stored;
	}
	return 'diesel';
}

function createFuelTypeStore() {
	const { subscribe, set, update } = writable<FuelType>(getInitial());

	return {
		subscribe,
		set: (value: FuelType) => {
			if (browser) {
				localStorage.setItem(STORAGE_KEY, value);
			}
			set(value);
		},
		update
	};
}

export const fuelType = createFuelTypeStore();

export const fuelTypeLabel = derived([fuelType, t], ([$fuelType, $t]) => {
	const labels: Record<FuelType, string> = {
		diesel: $t.map.diesel,
		e5: $t.map.e5,
		e10: $t.map.e10
	};
	return labels[$fuelType];
});
