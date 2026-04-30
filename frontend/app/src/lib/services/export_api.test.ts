import { test, expect, beforeEach, vi } from 'vitest';

const mockBlob = new Blob(['test data'], { type: 'application/json' });

const mockFetch = vi.fn();

vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

test('exportAsJson sends authorization header and returns blob', async () => {
	const { exportAsJson } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		blob: () => Promise.resolve(mockBlob)
	});

	const result = await exportAsJson('test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/export/json'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toBe(mockBlob);
});

test('exportAsJson throws error on failure', async () => {
	const { exportAsJson } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Unauthorized' })
	});

	await expect(exportAsJson('invalid-token')).rejects.toThrow('Unauthorized');
});

test('exportAsJson handles generic error response', async () => {
	const { exportAsJson } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(exportAsJson('test-token')).rejects.toThrow('Export failed');
});

test('exportAsCsv sends authorization header and returns blob', async () => {
	const { exportAsCsv } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: true,
		blob: () => Promise.resolve(mockBlob)
	});

	const result = await exportAsCsv('test-token-12345');

	expect(mockFetch).toHaveBeenCalledWith(
		expect.stringContaining('/export/csv'),
		expect.objectContaining({
			headers: expect.objectContaining({
				Authorization: 'Bearer test-token-12345'
			})
		})
	);
	expect(result).toBe(mockBlob);
});

test('exportAsCsv throws error on failure', async () => {
	const { exportAsCsv } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ detail: 'Database unavailable' })
	});

	await expect(exportAsCsv('invalid-token')).rejects.toThrow('Database unavailable');
});

test('exportAsCsv handles malformed error JSON', async () => {
	const { exportAsCsv } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.reject(new Error('Parse error'))
	});

	await expect(exportAsCsv('test-token')).rejects.toThrow('Export failed');
});
