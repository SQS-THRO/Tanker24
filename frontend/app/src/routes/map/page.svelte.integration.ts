import { expect, test } from '@playwright/test';

test('shows auth required modal when not logged in', async ({ page }) => {
	await page.goto('/map');

	// Dismiss the consent modal (always second in DOM order)
	await page.locator('.modal-overlay').last().locator('.btn-secondary').click();

	// AuthRequiredModal should remain (it has a .modal-icon the consent modal lacks)
	await expect(page.locator('.modal-overlay').filter({ has: page.locator('.modal-icon') })).toBeVisible();
});

test('map loads with controls and stations when authenticated', async ({ page }) => {
	const email = `test-${Date.now()}@example.com`;
	const password = `Pw-${crypto.randomUUID()}!`;

	await page.goto('/register');
	await page.locator('.modal-overlay .btn-secondary').click();
	await page.fill('#first_name', 'Test');
	await page.fill('#last_name', 'User');
	await page.fill('#email', email);
	await page.fill('#password', password);
	await page.fill('#confirmPassword', password);
	await page.fill('#invitationKey', '901563b82fa7adcbbc2a7e885f143c57');
	await page.click('button[type="submit"]');
	await page.waitForURL('**/map');

	await expect(page.locator('.map-container')).toBeVisible();
	await expect(page.locator('.leaflet-container')).toBeVisible({ timeout: 10000 });
	await expect(page.locator('.zoom-controls')).toBeVisible();
	await expect(page.locator('.location-btn')).toBeVisible();
	await expect(page.locator('.nearby-station-marker').first()).toBeVisible({ timeout: 10000 }); //one or more markers on the map are available -> stations are shown
});
