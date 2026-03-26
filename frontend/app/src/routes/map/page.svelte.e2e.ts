import { expect, test } from '@playwright/test';

test('redirects to login when not authenticated', async ({ page }) => {
	await page.goto('/map');
	await expect(page).toHaveURL(/.*\/login/);
});
