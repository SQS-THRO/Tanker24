import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';

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

test('exportAsJson throws fallback error when response has no detail', async () => {
	const { exportAsJson } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ message: 'Forbidden' })
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

test('exportAsCsv throws fallback error when response has no detail', async () => {
	const { exportAsCsv } = await import('./export_api');

	mockFetch.mockResolvedValueOnce({
		ok: false,
		json: () => Promise.resolve({ message: 'Server error' })
	});

	await expect(exportAsCsv('test-token')).rejects.toThrow('Export failed');
});

// downloadBlob tests - requires DOM mocking
describe('downloadBlob', () => {
	let createObjectURLMock: ReturnType<typeof vi.fn>;
	let revokeObjectURLMock: ReturnType<typeof vi.fn>;
	let mockAnchor: {
		href: string;
		download: string;
		click: ReturnType<typeof vi.fn>;
		remove: ReturnType<typeof vi.fn>;
	};

	beforeEach(() => {
		// Reset fetch mock
		mockFetch.mockReset();

		// Create fresh mocks for each test
		createObjectURLMock = vi.fn(() => 'blob-url-123');
		revokeObjectURLMock = vi.fn();

		mockAnchor = {
			href: '',
			download: '',
			click: vi.fn(),
			remove: vi.fn()
		};

		// Create mock document
		const mockDocument = {
			body: {
				appendChild: vi.fn(() => mockAnchor),
				removeChild: vi.fn()
			},
			createElement: vi.fn(() => mockAnchor)
		};

		// Stub globals
		vi.stubGlobal('document', mockDocument as unknown as Document);

		// Stub URL as a plain object with methods
		vi.stubGlobal('URL', {
			createObjectURL: createObjectURLMock,
			revokeObjectURL: revokeObjectURLMock
		} as unknown as typeof URL);
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	test('creates object URL from blob using globalThis.URL', async () => {
		const { downloadBlob } = await import('./export_api');
		const blob = new Blob(['test data'], { type: 'text/plain' });

		downloadBlob(blob, 'test.txt');

		expect(createObjectURLMock).toHaveBeenCalledWith(blob);
	});

	test('creates anchor element with correct attributes', async () => {
		const { downloadBlob } = await import('./export_api');
		const blob = new Blob(['test data'], { type: 'text/plain' });

		downloadBlob(blob, 'test.txt');

		// Verify createElement was called with 'a'
		expect((globalThis.document as typeof mockDocument).createElement).toHaveBeenCalledWith('a');

		// Verify anchor properties were set
		expect(mockAnchor.href).toBe('blob-url-123');
		expect(mockAnchor.download).toBe('test.txt');
	});

	test('appends anchor to body and triggers click', async () => {
		const { downloadBlob } = await import('./export_api');
		const blob = new Blob(['test data'], { type: 'text/plain' });

		downloadBlob(blob, 'test.txt');

		expect((globalThis.document as typeof mockDocument).body.appendChild).toHaveBeenCalledWith(mockAnchor);
		expect(mockAnchor.click).toHaveBeenCalled();
	});

	test('removes anchor from DOM using modern remove() method', async () => {
		const { downloadBlob } = await import('./export_api');
		const blob = new Blob(['test data'], { type: 'text/plain' });

		downloadBlob(blob, 'test.txt');

		// Verify remove() was called on the anchor (modern approach)
		expect(mockAnchor.remove).toHaveBeenCalled();
	});

	test('revokes object URL after download', async () => {
		const { downloadBlob } = await import('./export_api');
		const blob = new Blob(['test data'], { type: 'text/plain' });

		downloadBlob(blob, 'test.txt');

		expect(revokeObjectURLMock).toHaveBeenCalledWith('blob-url-123');
	});

	test('handles different file types correctly', async () => {
		const { downloadBlob } = await import('./export_api');

		const testCases = [
			{ blob: new Blob(['{"key": "value"}'], { type: 'application/json' }), filename: 'data.json' },
			{ blob: new Blob(['col1,col2\nval1,val2'], { type: 'text/csv' }), filename: 'data.csv' },
			{ blob: new Blob(['<html></html>'], { type: 'text/html' }), filename: 'page.html' }
		];

		for (const { blob, filename } of testCases) {
			createObjectURLMock.mockClear();
			revokeObjectURLMock.mockClear();
			mockAnchor.remove.mockClear();

			downloadBlob(blob, filename);

			expect(createObjectURLMock).toHaveBeenCalledWith(blob);
			expect(revokeObjectURLMock).toHaveBeenCalled();
			// Each file type should trigger the same workflow
			expect(mockAnchor.remove).toHaveBeenCalled();
		}
	});

	test('uses globalThis.URL instead of window.URL', async () => {
		const { downloadBlob } = await import('./export_api');
		const blob = new Blob(['test'], { type: 'text/plain' });

		// Verify URL is accessed via globalThis
		const urlSpy = vi.spyOn(globalThis.URL, 'createObjectURL');

		downloadBlob(blob, 'test.txt');

		// Verify createObjectURL was called on globalThis.URL
		expect(urlSpy).toHaveBeenCalled();
	});
});
