import { expect, test, type Page } from '@playwright/test';

async function dismissConsentModal(page: Page) {
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

test('shows auth modal when not authenticated', async ({ page }) => {
	await page.goto('/map');
	await dismissConsentModal(page);
	await expect(page.locator('.modal-overlay')).toBeVisible();
	await expect(page.locator('.modal-title')).toContainText('Login Required');
});

test('back button returns to previous page', async ({ page }) => {
	await page.goto('/map');
	await dismissConsentModal(page);
	await page.goto('/');
	await page.click('text=Explore Map');
	await page.locator('.modal-overlay .btn-secondary').click();
	await expect(page).toHaveURL('/');
});

test('login button navigates to login page', async ({ page }) => {
	await page.goto('/map');
	await dismissConsentModal(page);
	await page.locator('.modal-overlay .btn-primary').click();
	await expect(page).toHaveURL(/\/login$/);
});
