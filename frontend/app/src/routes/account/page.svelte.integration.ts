import { expect, test } from '@playwright/test';

test.describe('account flow', () => {
	const password = `Pw-${crypto.randomUUID()}!`;
	let email: string;

	test.beforeEach(async ({ page }) => {
		email = `test-${Date.now()}@example.com`;

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
		await page.goto('/account');
		await page.waitForURL('**/account');
		await page.locator('.modal-overlay .btn-secondary').click();
	});

	test('can log in with valid credentials', async ({ page }) => {
		await page.click('.btn-danger');
		await page.waitForURL('**/');

		await page.goto('/login');
		await page.locator('.modal-overlay .btn-secondary').click();

		await page.fill('#email', email);
		await page.fill('#password', password);
		await page.click('button[type="submit"]');
		await page.waitForFunction(() => localStorage.getItem('token') !== null, { timeout: 15000 });
		await page.goto('/account');
		await page.waitForURL('**/account');
		await page.locator('.modal-overlay .btn-secondary').click();
		await expect(page.locator('.profile-header')).toBeVisible();
	});

	test('account page sections are visible', async ({ page }) => {
		await expect(page.locator('.profile-header')).toBeVisible();
		await expect(page.locator('.theme-settings')).toBeVisible();
		await expect(page.locator('.stats-card')).toBeVisible();
		await expect(page.locator('.tanking-section')).toBeVisible();
		await expect(page.locator('.export-section')).toBeVisible();
		await expect(page.locator('.actions-section:not(.danger-zone)')).toBeVisible();
		await expect(page.locator('.btn-danger')).toBeVisible();
	});

	test('can log out', async ({ page }) => {
		await page.click('.btn-danger');
		await page.waitForURL('**/');
		await expect(page.locator('h1')).toBeVisible();
	});
});
