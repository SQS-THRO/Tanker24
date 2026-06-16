import { expect, test } from '@playwright/test';
import { dismissConsentModal } from '../test-utils.e2e';

test.beforeEach(async ({ page }) => {
	await page.goto('/impressum');
	await dismissConsentModal(page);
});

test('renders legal notice heading', async ({ page }) => {
	await expect(page.locator('h1')).toBeVisible();
});

test('renders contact and copyright sections', async ({ page }) => {
	await expect(page.locator('text=Contact')).toBeVisible();
	await expect(page.locator('text=Copyright')).toBeVisible();
});

test('privacy policy link navigates to /privacy', async ({ page }) => {
	await page.locator('a.impressum-text').click();
	await expect(page).toHaveURL(/\/privacy$/);
});
