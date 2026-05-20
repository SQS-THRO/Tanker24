import { request } from '$lib/utils/request';

export interface User {
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

		return request<AuthResponse>('/auth/jwt/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: formData,
			fallbackError: 'Login failed'
		});
	},

	async logout(token: string): Promise<void> {
		await request<void>('/auth/jwt/logout', {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${token}`
			},
			fallbackError: 'Logout failed'
		});
	},

	async getCurrentUser(token: string): Promise<User> {
		return request<User>('/users/me', {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
	}
};
