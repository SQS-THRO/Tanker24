import type { Page } from '@playwright/test';

export async function dismissConsentModal(page: Page) {
	const consentModal = page.locator('[role="dialog"]', { hasText: 'Data Usage' });
	const isVisible = await consentModal.isVisible();
	if (isVisible) {
		await consentModal.locator('button', { hasText: 'Accept' }).click();
		try {
			await consentModal.waitFor({ state: 'hidden', timeout: 5000 });
		} catch {
			// Modal may have been removed from DOM
		}
	}
}
