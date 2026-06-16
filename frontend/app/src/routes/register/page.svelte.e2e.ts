import { expect, test } from '@playwright/test';
import { dismissConsentModal } from '../test-utils.e2e';

test.beforeEach(async ({ page }) => {
	await page.goto('/register');
	await dismissConsentModal(page);
});

test('renders registration form with all fields', async ({ page }) => {
	await expect(page.locator('h1')).toBeVisible();
	await expect(page.locator('#first_name')).toBeVisible();
	await expect(page.locator('#last_name')).toBeVisible();
	await expect(page.locator('#email')).toBeVisible();
	await expect(page.locator('#password')).toBeVisible();
	await expect(page.locator('#confirmPassword')).toBeVisible();
	await expect(page.locator('#invitationKey')).toBeVisible();
	await expect(page.locator('button[type="submit"]')).toBeVisible();
});

test('shows validation error for invalid email', async ({ page }) => {
	const emailInput = page.locator('#email');
	await emailInput.fill('bad-email');
	await expect(page.locator('.field-error-wrapper.visible .field-error')).toContainText('valid email');
});

test('password strength checklist appears on focus', async ({ page }) => {
	await page.locator('#password').focus();
	await expect(page.locator('.password-checklist')).toBeVisible();
});

test('password visibility toggle works', async ({ page }) => {
	const passwordInput = page.locator('#password');
	await passwordInput.fill('mysecret');
	await expect(passwordInput).toHaveAttribute('type', 'password');
	await page.locator('.toggle-password').first().click();
	await expect(passwordInput).toHaveAttribute('type', 'text');
});

test('confirm password mismatch shows error', async ({ page }) => {
	await page.locator('#password').fill('ValidP@ss1');
	await page.locator('#confirmPassword').fill('DifferentP@ss1');
	await page.locator('#confirmPassword').blur();
	await expect(page.locator('.field-error-wrapper.visible .field-error')).toContainText('do not match');
});

test('Sign in link navigates to /login', async ({ page }) => {
	await page.locator('.auth-card a[href="/login"]').click();
	await expect(page).toHaveURL(/\/login$/);
});

test('submit button is visually disabled when form is incomplete', async ({ page }) => {
	const submitBtn = page.locator('button[type="submit"]');
	await expect(submitBtn).toBeDisabled();
	await expect(submitBtn).toHaveCSS('opacity', '0.5');
	await expect(submitBtn).toHaveCSS('cursor', 'not-allowed');
});
