import { expect, test } from '@playwright/test';
import { dismissConsentModal } from '../test-utils.e2e';

test.beforeEach(async ({ page }) => {
	await page.goto('/privacy');
	await dismissConsentModal(page);
});

test('renders privacy policy heading', async ({ page }) => {
	await expect(page.locator('h1')).toBeVisible();
});

test('renders all section headings', async ({ page }) => {
	const sections = [
		'Controller',
		'Collection of General Data',
		'Purpose of Processing',
		'Legal Basis',
		'Recipients of Personal Data',
		'Retention Period',
		'Your Rights',
		'Withdrawal of Consent',
		'Right to Lodge a Complaint',
		'External Links',
		'Amendment of this Privacy Policy'
	];
	for (const section of sections) {
		await expect(page.locator(`h2:has-text("${section}")`)).toBeVisible();
	}
});
