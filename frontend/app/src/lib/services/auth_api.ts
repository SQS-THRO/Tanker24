import { request } from '$lib/utils/request';
import { env } from '$env/dynamic/public';

const API_BASE = (env.PUBLIC_BACKEND_URL ?? 'http://127.0.0.1:8000') + '/api/v0';

interface User {
	id: number;
	email: string;
	forename: string;
	surname: string;
	is_active: boolean;
	is_superuser: boolean;
	is_verified: boolean;
}

interface AuthResponse {
	access_token: string;
	token_type: string;
}

interface RegisterData {
	email: string;
	forename: string;
	surname: string;
	password: string;
	invitation_key: string;
}

interface LoginData {
	email: string;
	password: string;
}

export const authService = {
	async register(data: RegisterData): Promise<User> {
		return request<User>('/auth/register', {
			method: 'POST',
			body: JSON.stringify(data)
		});
	},

	async login(data: LoginData): Promise<AuthResponse> {
		const formData = new URLSearchParams();
		formData.append('username', data.email);
		formData.append('password', data.password);

		const response = await fetch(`${API_BASE}/auth/jwt/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: formData
		});

		if (!response.ok) {
			const error = await response.json().catch(() => ({ detail: 'Login failed' }));
			throw new Error(error.detail || 'Login failed');
		}

		return response.json();
	},

	async logout(): Promise<void> {
		await fetch(`${API_BASE}/auth/jwt/logout`, { method: 'POST' });
	},

	async getCurrentUser(token: string): Promise<User> {
		return request<User>('/users/me', {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
	}
};
