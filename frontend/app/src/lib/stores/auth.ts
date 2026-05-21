import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { authService } from '$lib/services/auth_api';
import type { User } from '$lib/services/auth_api';

interface AuthState {
	user: User | null;
	loading: boolean;
	error: string | null;
}

function getToken(): string | null {
	if (!browser) return null;
	return localStorage.getItem('token');
}

function setToken(token: string | null) {
	if (!browser) return;
	if (token) {
		localStorage.setItem('token', token);
	} else {
		localStorage.removeItem('token');
	}
}

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		loading: true,
		error: null
	});

	return {
		subscribe,
		setToken,

		async checkAuth(): Promise<void> {
			const token = getToken();
			if (!token) {
				set({ user: null, loading: false, error: null });
				return;
			}

			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const user = await authService.getCurrentUser(token);
				set({ user, loading: false, error: null });
			} catch {
				setToken(null);
				set({ user: null, loading: false, error: null });
			}
		},

		async login(email: string, password: string): Promise<void> {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const response = await authService.login({ email, password });
				setToken(response.access_token);
				const user = await authService.getCurrentUser(response.access_token);
				set({ user, loading: false, error: null });
			} catch (e) {
				const message = e instanceof Error ? e.message : 'Login failed';
				update((state) => ({ ...state, loading: false, error: message }));
				throw e;
			}
		},

		async register(data: { email: string; forename: string; surname: string; password: string; invitation_key: string }): Promise<void> {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				await authService.register(data);
				update((state) => ({ ...state, loading: false }));
			} catch (e) {
				const message = e instanceof Error ? e.message : 'Registration failed';
				update((state) => ({ ...state, loading: false, error: message }));
				throw e;
			}
		},

		async logout(): Promise<void> {
			const token = getToken();
			try {
				if (token) {
					await authService.logout(token);
				}
			} catch {
				// proceed with local logout even if server call fails
			}
			setToken(null);
			set({ user: null, loading: false, error: null });
		}
	};
}

export const auth = createAuthStore();

export const isAuthenticated = derived(auth, ($auth) => $auth.user !== null);
