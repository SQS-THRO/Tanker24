import { expect, test } from '@playwright/test';
import { dismissConsentModal } from '../test-utils.e2e';

test.beforeEach(async ({ page }) => {
	await page.goto('/login');
	await dismissConsentModal(page);
});

test('renders login form with email, password, and submit button', async ({ page }) => {
	await expect(page.locator('h1')).toBeVisible();
	await expect(page.locator('#email')).toBeVisible();
	await expect(page.locator('#password')).toBeVisible();
	await expect(page.locator('button[type="submit"]')).toBeVisible();
});

test('shows validation error for invalid email format', async ({ page }) => {
	const emailInput = page.locator('#email');
	await emailInput.fill('not-an-email');
	await emailInput.blur();
	await expect(page.locator('.field-error')).toBeVisible();
});

test('submit button is visually disabled when fields are empty', async ({ page }) => {
	const submitBtn = page.locator('button[type="submit"]');
	await expect(submitBtn).toBeDisabled();
	await expect(submitBtn).toHaveCSS('opacity', '0.5');
	await expect(submitBtn).toHaveCSS('cursor', 'not-allowed');
});

test('submit button becomes enabled when both fields are filled', async ({ page }) => {
	await page.locator('#email').fill('test@example.com');
	await page.locator('#password').fill('somepassword');
	await expect(page.locator('button[type="submit"]')).toBeEnabled();
});

test('password visibility toggle works', async ({ page }) => {
	const passwordInput = page.locator('#password');
	await passwordInput.fill('mysecretpassword');
	await expect(passwordInput).toHaveAttribute('type', 'password');
	await page.locator('.toggle-password').first().click();
	await expect(passwordInput).toHaveAttribute('type', 'text');
});

test('Create one link navigates to /register', async ({ page }) => {
	await page.locator('text=Create one').click();
	await expect(page).toHaveURL(/\/register$/);
});
