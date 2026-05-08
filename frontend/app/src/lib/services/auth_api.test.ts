import { test, expect, beforeEach, vi } from 'vitest';

const userFixture = {
	id: 1,
	email: 'test@example.com',
	forename: 'Test',
	surname: 'User',
	is_active: true,
	is_superuser: false,
	is_verified: true
};

const authResponseFixture = {
	access_token: 'test-token-12345',
	token_type: 'bearer'
};

const registerDataFixture = {
	email: 'test@example.com',
	forename: 'Test',
	surname: 'User',
	password: 'securePassword123'
};

const loginDataFixture = {
	email: 'test@example.com',
	password: 'securePassword123'
};

const registerDataWithKeyFixture = {
	email: 'test@example.com',
	forename: 'Test',
	surname: 'User',
	password: 'securePassword123',
	invitation_key: 'a'.repeat(32)
};

const mockFetch = vi.fn();

vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

test('register sends correct data to API', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(userFixture)
	});

	const result = await authService.register(registerDataFixture);

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/auth/register'),
		expect.objectContaining({
			method: 'POST',
			headers: expect.objectContaining({
				'Content-Type': 'application/json'
			}),
			body: JSON.stringify(registerDataFixture)
		})
	);
	expect(result).toEqual(userFixture);
});

test('register throws error on failure', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Email already exists' })
	});

	await expect(authService.register(registerDataFixture)).rejects.toThrow('Email already exists');
});

test('register parses generic error when JSON has no detail', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ message: 'Server error' })
	});

	await expect(authService.register(registerDataFixture)).rejects.toThrow('Request failed');
});

test('register handles malformed error JSON', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(authService.register(registerDataFixture)).rejects.toThrow('Request failed');
});

test('login sends form data to correct endpoint', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(authResponseFixture)
	});

	const result = await authService.login(loginDataFixture);

	const call = mockFetch.mock.calls[0];
	expect(call[0]).toContain('/auth/jwt/login');
	expect(call[1].method).toBe('POST');
	expect(call[1].headers['Content-Type']).toBe('application/x-www-form-urlencoded');
	const body = call[1].body as URLSearchParams;
	expect(body.get('username')).toBe(loginDataFixture.email);
	expect(body.get('password')).toBe(loginDataFixture.password);
	expect(result).toEqual(authResponseFixture);
});

test('login throws error on failure', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Invalid credentials' })
	});

	await expect(authService.login(loginDataFixture)).rejects.toThrow('Invalid credentials');
});

test('login throws fallback error when response has no detail', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		status: 401,
		json: () => Promise.resolve({ message: 'Unauthorized' })
	});

	await expect(authService.login(loginDataFixture)).rejects.toThrow('Login failed');
});

test('login throws fallback error when response JSON is malformed', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		status: 500,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(authService.login(loginDataFixture)).rejects.toThrow('Login failed');
});

test('logout calls correct endpoint', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: true
	});

	await authService.logout();

	expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining('/auth/jwt/logout'), expect.objectContaining({ method: 'POST' }));
});

test('logout does not throw on failure', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false
	});

	await expect(authService.logout()).resolves.toBeUndefined();
});

test('getCurrentUser sends authorization header', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(userFixture)
	});

	const result = await authService.getCurrentUser('test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/users/me'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toEqual(userFixture);
});

test('getCurrentUser throws error on failure', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Unauthorized' })
	});

	await expect(authService.getCurrentUser('invalid-token')).rejects.toThrow('Unauthorized');
});

test('register sends invitation_key to API', async () => {
	const { authService } = await import('./auth_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(userFixture)
	});

	await authService.register(registerDataWithKeyFixture);

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/auth/register'),
		expect.objectContaining({
			method: 'POST',
			headers: expect.objectContaining({
				'Content-Type': 'application/json'
			}),
			body: JSON.stringify(registerDataWithKeyFixture)
		})
	);
});
