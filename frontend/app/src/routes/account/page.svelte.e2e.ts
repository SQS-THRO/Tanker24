import { expect, test } from '@playwright/test';
import { dismissConsentModal } from '../test-utils.e2e';

test('redirects to /login when not authenticated', async ({ page }) => {
	await page.goto('/account');
	await dismissConsentModal(page);
	await page.waitForURL(/\/login$/);
	await expect(page).toHaveURL(/\/login$/);
});

test('redirects to /login when API call fails with fake token', async ({ page }) => {
	await page.goto('/account');
	await dismissConsentModal(page);
	await page.evaluate(() => localStorage.setItem('token', 'fake-token'));
	await page.reload();
	await page.waitForURL(/\/login$/, { timeout: 15000 });
	await expect(page.locator('h1')).toBeVisible();
});
