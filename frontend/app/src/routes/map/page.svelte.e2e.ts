import { expect, test } from '@playwright/test';

test('has expected h1', async ({ page }) => {
	await page.goto('/map');
	await expect(page.locator('h3')).toBeVisible();
});
