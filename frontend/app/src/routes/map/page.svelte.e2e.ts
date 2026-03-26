import { expect, test } from '@playwright/test';

test('has expected heading', async ({ page }) => {
	await page.goto('/map');
	await expect(page.locator('.map-header')).toBeVisible();
});
