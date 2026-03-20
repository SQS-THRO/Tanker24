import { test, expect, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Button from '$lib/components/button.svelte';

vi.mock('$app/navigation', () => ({
	goto: vi.fn(),
	resolve: (href: string) => href
}));

test('Button redirects to href when clicked', async () => {
	const { getByRole } = render(Button, { props: { label: 'Click me', href: '/test' } });
	const button = getByRole('button', { name: 'Click me' });
	await button.click();
	const goto = vi.mocked((await import('$app/navigation')).goto);
	expect(goto).toHaveBeenCalled();
});
