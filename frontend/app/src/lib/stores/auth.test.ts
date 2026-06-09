import { test, expect, describe, beforeEach, afterEach, vi } from 'vitest';
import { get } from 'svelte/store';

const mockLocalStorage = {
	getItem: vi.fn().mockReturnValue(null),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

vi.stubGlobal('localStorage', mockLocalStorage);

const mockEnv = { browser: true };

vi.mock('$app/environment', () => mockEnv);

const mockUser = {
	id: 1,
	email: 'test@example.com',
	forename: 'John',
	surname: 'Doe',
	is_active: true,
	is_superuser: false,
	is_verified: true
};

const mockToken = 'mock-jwt-token';

const mockAuthService = {
	getCurrentUser: vi.fn(),
	login: vi.fn(),
	logout: vi.fn(),
	register: vi.fn()
};

vi.mock('$lib/services/auth_api', () => ({
	authService: mockAuthService
}));

beforeEach(() => {
	mockLocalStorage.getItem.mockReset();
	mockLocalStorage.setItem.mockReset();
	mockLocalStorage.removeItem.mockReset();
	mockAuthService.getCurrentUser.mockReset();
	mockAuthService.login.mockReset();
	mockAuthService.logout.mockReset();
	mockAuthService.register.mockReset();
});

describe('auth store', () => {
	afterEach(() => {
		vi.resetModules();
	});

	test('initializes with loading:true when no stored token', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(state.loading).toBe(true);
		expect(state.error).toBeNull();
	});

	test('checkAuth sets loading:false and null user when no token', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.checkAuth();
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(state.loading).toBe(false);
		expect(mockAuthService.getCurrentUser).not.toHaveBeenCalled();
	});

	test('checkAuth fetches user when token exists', async () => {
		mockLocalStorage.getItem.mockReturnValue(mockToken);
		mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.checkAuth();
		const state = get(auth);
		expect(state.user).toEqual(mockUser);
		expect(state.loading).toBe(false);
		expect(mockAuthService.getCurrentUser).toHaveBeenCalledWith(mockToken);
	});

	test('checkAuth clears token and user when getCurrentUser fails', async () => {
		mockLocalStorage.getItem.mockReturnValue(mockToken);
		mockAuthService.getCurrentUser.mockRejectedValue(new Error('Unauthorized'));
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.checkAuth();
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(state.loading).toBe(false);
		expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
	});

	test('login succeeds and sets user', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		mockAuthService.login.mockResolvedValue({ access_token: mockToken, token_type: 'bearer' });
		mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.login('test@example.com', 'password');
		const state = get(auth);
		expect(state.user).toEqual(mockUser);
		expect(state.loading).toBe(false);
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', mockToken);
	});

	test('login sets error on failure', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		mockAuthService.login.mockRejectedValue(new Error('Invalid credentials'));
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await expect(auth.login('test@example.com', 'wrong')).rejects.toThrow('Invalid credentials');
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(state.loading).toBe(false);
		expect(state.error).toBe('Invalid credentials');
	});

	test('register succeeds', async () => {
		mockAuthService.register.mockResolvedValue(mockUser);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		const data = { email: 'new@example.com', forename: 'Jane', surname: 'Doe', password: 'secret123', invitation_key: 'invite-key' };
		await auth.register(data);
		expect(mockAuthService.register).toHaveBeenCalledWith(data);
		const state = get(auth);
		expect(state.loading).toBe(false);
	});

	test('register sets error on failure', async () => {
		mockAuthService.register.mockRejectedValue(new Error('Email already taken'));
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		const data = { email: 'existing@example.com', forename: 'Jane', surname: 'Doe', password: 'secret123', invitation_key: 'invite-key' };
		await expect(auth.register(data)).rejects.toThrow('Email already taken');
		const state = get(auth);
		expect(state.error).toBe('Email already taken');
		expect(state.loading).toBe(false);
	});

	test('logout clears user and token', async () => {
		mockLocalStorage.getItem.mockReturnValue(mockToken);
		mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
		mockAuthService.logout.mockResolvedValue(undefined);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.checkAuth();
		expect(get(auth).user).toEqual(mockUser);
		await auth.logout();
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(state.loading).toBe(false);
		expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
		expect(mockAuthService.logout).toHaveBeenCalled();
	});

	test('logout proceeds with local cleanup even if server call fails', async () => {
		mockAuthService.logout.mockRejectedValue(new Error('Network error'));
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.logout();
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
	});

	test('setToken stores token in localStorage', async () => {
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		auth.setToken(mockToken);
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', mockToken);
	});

	test('setToken removes token from localStorage when called with null', async () => {
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		auth.setToken(mockToken);
		auth.setToken(null);
		expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
	});
});

describe('isAuthenticated derived store', () => {
	afterEach(() => {
		vi.resetModules();
	});

	test('is false when user is null', async () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		vi.resetModules();
		const { auth, isAuthenticated } = await import('$lib/stores/auth');
		await auth.checkAuth();
		expect(get(isAuthenticated)).toBe(false);
	});

	test('is true when user is set', async () => {
		mockLocalStorage.getItem.mockReturnValue(mockToken);
		mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
		vi.resetModules();
		const { auth, isAuthenticated } = await import('$lib/stores/auth');
		await auth.checkAuth();
		expect(get(isAuthenticated)).toBe(true);
	});
});

describe('auth store in non-browser environment', () => {
	beforeEach(() => {
		mockEnv.browser = false;
	});

	afterEach(() => {
		mockEnv.browser = true;
		vi.resetModules();
	});

	test('initializes without calling localStorage', async () => {
		mockLocalStorage.getItem.mockClear();
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		const state = get(auth);
		expect(state.user).toBeNull();
		expect(state.loading).toBe(true);
		expect(mockLocalStorage.getItem).not.toHaveBeenCalled();
	});

	test('checkAuth does not call localStorage when no browser', async () => {
		mockLocalStorage.getItem.mockClear();
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.checkAuth();
		expect(mockLocalStorage.getItem).not.toHaveBeenCalled();
	});

	test('setToken does not write to localStorage', async () => {
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		auth.setToken(mockToken);
		expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
	});

	test('logout does not call localStorage removeItem', async () => {
		mockAuthService.logout.mockResolvedValue(undefined);
		vi.resetModules();
		const { auth } = await import('$lib/stores/auth');
		await auth.logout();
		expect(mockLocalStorage.removeItem).not.toHaveBeenCalled();
	});
});
