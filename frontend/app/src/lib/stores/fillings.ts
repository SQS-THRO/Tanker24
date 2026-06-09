import { writable } from 'svelte/store';
import { getFillings, deleteFilling, createFilling, type FillingRecord, type CreateFillingPayload } from '$lib/services/fillings_api';

interface FillingsState {
	data: FillingRecord[];
	loading: boolean;
	error: string | null;
}

function createFillingsStore() {
	const { subscribe, set, update } = writable<FillingsState>({
		data: [],
		loading: false,
		error: null
	});

	return {
		subscribe,

		async fetchFillings(token: string): Promise<void> {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const data = await getFillings(token);
				set({ data, loading: false, error: null });
			} catch (e) {
				const message = e instanceof Error ? e.message : 'Failed to load fillings';
				update((state) => ({ ...state, loading: false, error: message }));
			}
		},

		async removeFilling(token: string, fillingId: number): Promise<void> {
			try {
				await deleteFilling(token, fillingId);
				update((state) => ({
					...state,
					data: state.data.filter((f) => f.id !== fillingId)
				}));
			} catch (e) {
				const message = e instanceof Error ? e.message : 'Failed to delete filling';
				throw new Error(message);
			}
		},

		async createFilling(token: string, payload: CreateFillingPayload): Promise<void> {
			await createFilling(token, payload);
		}
	};
}

export const fillings = createFillingsStore();
