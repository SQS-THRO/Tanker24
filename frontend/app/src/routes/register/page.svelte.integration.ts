import { expect, test } from '@playwright/test';

test('can register and will be logged in after', async ({ page }) => {
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

	await page.waitForFunction(() => localStorage.getItem('token') !== null, { timeout: 15000 });

	await page.waitForURL('**/map');

	await expect(page.locator('.map-container')).toBeVisible();
});
