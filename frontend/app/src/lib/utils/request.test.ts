import { test, expect, beforeEach, vi } from 'vitest';

const mockFetch = vi.fn();

vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

test('request includes JSON content-type header', async () => {
	const { request } = await import('$lib/utils/request');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve({ success: true })
	});

	await request('/test');

	const call = mockFetch.mock.calls[0];
	expect(call[1].headers['Content-Type']).toBe('application/json');
});

test('request merges custom headers with default headers', async () => {
	const { request } = await import('$lib/utils/request');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve({ success: true })
	});

	await request('/test', {
		headers: {
			Authorization: 'Bearer test-token'
		}
	});

	const call = mockFetch.mock.calls[0];
	expect(call[1].headers).toBeDefined();
	expect(call[1].headers['Authorization']).toBe('Bearer test-token');
});

test('request passes through options correctly', async () => {
	const { request } = await import('$lib/utils/request');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve({ success: true })
	});

	await request('/test', {
		method: 'POST',
		body: JSON.stringify({ key: 'value' }),
		credentials: 'include'
	});

	const call = mockFetch.mock.calls[0];
	expect(call[1].method).toBe('POST');
	expect(call[1].body).toBe('{"key":"value"}');
	expect(call[1].credentials).toBe('include');
});

test('request parses and returns JSON on success', async () => {
	const { request } = await import('$lib/utils/request');

	const responseData = { id: 1, name: 'Test' };
	mockFetch.mockResolvedValueOnce({
		ok: true,
		json: () => Promise.resolve(responseData)
	});

	const result = await request<typeof responseData>('/test');

	expect(result).toEqual(responseData);
});

test('request throws error with detail on failure response', async () => {
	const { request } = await import('$lib/utils/request');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Not found' })
	});

	await expect(request('/test')).rejects.toThrow('Not found');
});

test('request throws generic error when JSON has no detail', async () => {
	const { request } = await import('$lib/utils/request');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ message: 'Server error' })
	});

	await expect(request('/test')).rejects.toThrow('Request failed');
});

test('request handles malformed error JSON', async () => {
	const { request } = await import('$lib/utils/request');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(request('/test')).rejects.toThrow('Request failed');
});
