import { expect, test } from '@playwright/test';
import { dismissConsentModal } from './test-utils.e2e';

test('has expected h1', async ({ page }) => {
	await page.goto('/');
	await dismissConsentModal(page);
	await expect(page.locator('h1')).toBeVisible();
});

test('hero section renders with title and CTA buttons', async ({ page }) => {
	await page.goto('/');
	await dismissConsentModal(page);
	await expect(page.locator('.hero-subtitle')).toBeVisible();
	await expect(page.locator('text=Explore Map')).toBeVisible();
	await expect(page.locator('text=Create Account')).toBeVisible();
});

test('Explore Map button navigates to /map', async ({ page }) => {
	await page.goto('/');
	await dismissConsentModal(page);
	await page.locator('text=Explore Map').click();
	await expect(page).toHaveURL(/\/map$/);
});

test('Create Account button navigates to /register', async ({ page }) => {
	await page.goto('/');
	await dismissConsentModal(page);
	await page.locator('text=Create Account').click();
	await expect(page).toHaveURL(/\/register$/);
});

test('renders three feature cards', async ({ page }) => {
	await page.goto('/');
	await dismissConsentModal(page);
	const cards = page.locator('.feature-card');
	await expect(cards).toHaveCount(3);
});

test('CTA section Get Started links to /register', async ({ page }) => {
	await page.goto('/');
	await dismissConsentModal(page);
	await page.locator('text=Get Started Free').click();
	await expect(page).toHaveURL(/\/register$/);
});
