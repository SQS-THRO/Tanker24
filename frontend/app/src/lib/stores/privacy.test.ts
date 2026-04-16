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
});
