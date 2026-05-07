import { test, expect, describe, beforeEach, vi, afterEach } from 'vitest';
import { get } from 'svelte/store';

const mockLocalStorage = {
	getItem: vi.fn().mockReturnValue(null),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
};

vi.stubGlobal('localStorage', mockLocalStorage);

vi.stubGlobal('window', {});

describe('privacyStore', () => {
	beforeEach(() => {
		mockLocalStorage.getItem.mockReturnValue(null);
		mockLocalStorage.setItem.mockClear();
	});

	afterEach(() => {
		vi.resetModules();
	});

	test('initializes with default settings when no stored value', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(false);
		expect(settings.hidden).toBe(false);
	});

	test('initializes with stored settings from localStorage', async () => {
		mockLocalStorage.getItem.mockReturnValue(JSON.stringify({ analyticsAccepted: true, hidden: false }));
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(true);
	});

	test('acceptAnalytics updates store and localStorage', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		privacyStore.acceptAnalytics();
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(true);
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('privacy-settings', JSON.stringify({ analyticsAccepted: true, hidden: false }));
	});

	test('declineAnalytics updates store with hidden and localStorage', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		privacyStore.declineAnalytics();
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(false);
		expect(settings.hidden).toBe(true);
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith('privacy-settings', JSON.stringify({ analyticsAccepted: false, hidden: true }));
	});

	test('reset restores default settings', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		privacyStore.acceptAnalytics();
		privacyStore.declineAnalytics();
		privacyStore.reset();
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(false);
		expect(settings.hidden).toBe(false);
	});

	test('hidden is reset to false on load', async () => {
		mockLocalStorage.getItem.mockReturnValue(JSON.stringify({ analyticsAccepted: false, hidden: true }));
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.hidden).toBe(false);
	});

	test('preserves analyticsAccepted when resetting hidden', async () => {
		mockLocalStorage.getItem.mockReturnValue(JSON.stringify({ analyticsAccepted: true, hidden: true }));
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(true);
		expect(settings.hidden).toBe(false);
	});

	test('falls back to defaults when stored JSON is corrupt', async () => {
		mockLocalStorage.getItem.mockReturnValue('not-valid-json');
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(false);
		expect(settings.hidden).toBe(false);
	});

	test('falls back to defaults when stored value is null', async () => {
		mockLocalStorage.getItem.mockReturnValue('null');
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(false);
		expect(settings.hidden).toBe(false);
	});

	test('reset persists defaults to localStorage', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		mockLocalStorage.setItem.mockClear();
		privacyStore.acceptAnalytics();
		privacyStore.reset();
		expect(mockLocalStorage.setItem).toHaveBeenLastCalledWith('privacy-settings', JSON.stringify({ analyticsAccepted: false, hidden: false }));
	});

	test('declineAnalytics persists hidden:true to localStorage', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		mockLocalStorage.setItem.mockClear();
		privacyStore.declineAnalytics();
		expect(mockLocalStorage.setItem).toHaveBeenLastCalledWith('privacy-settings', JSON.stringify({ analyticsAccepted: false, hidden: true }));
	});

	test('acceptAnalytics after decline sets analyticsAccepted but keeps hidden', async () => {
		const { privacyStore } = await import('$lib/stores/privacy');
		privacyStore.declineAnalytics();
		privacyStore.acceptAnalytics();
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(true);
		expect(settings.hidden).toBe(true);
	});
});

describe('privacyStore in non-browser environment', () => {
	beforeEach(() => {
		vi.stubGlobal('window', undefined);
	});

	afterEach(() => {
		vi.stubGlobal('window', {});
		vi.resetModules();
	});

	test('initializes with default settings without calling localStorage', async () => {
		mockLocalStorage.getItem.mockClear();
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		const settings = get(privacyStore);
		expect(settings.analyticsAccepted).toBe(false);
		expect(settings.hidden).toBe(false);
		expect(mockLocalStorage.getItem).not.toHaveBeenCalled();
	});

	test('acceptAnalytics does not write to localStorage', async () => {
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		mockLocalStorage.setItem.mockClear();
		privacyStore.acceptAnalytics();
		expect(get(privacyStore).analyticsAccepted).toBe(true);
		expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
	});

	test('declineAnalytics does not write to localStorage', async () => {
		vi.resetModules();
		const { privacyStore } = await import('$lib/stores/privacy');
		mockLocalStorage.setItem.mockClear();
		privacyStore.declineAnalytics();
		expect(get(privacyStore).hidden).toBe(true);
		expect(mockLocalStorage.setItem).not.toHaveBeenCalled();
	});
});
