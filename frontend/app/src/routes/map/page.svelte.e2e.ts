import { expect, test } from '@playwright/test';
import { dismissConsentModal } from '../test-utils.e2e';

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
