<script lang="ts">
	import { locale } from '$lib/stores/locale';

	let showDropdown = $state(false);

	function setLocale(lang: 'en' | 'de') {
		locale.set(lang);
		showDropdown = false;
	}
</script>

<div class="lang-switcher">
	<button class="lang-btn" onclick={() => (showDropdown = !showDropdown)}>
		<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<circle cx="12" cy="12" r="10" />
			<line x1="2" y1="12" x2="22" y2="12" />
			<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
		</svg>
		<span class="lang-code">{$locale.toUpperCase()}</span>
		<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<path d="M6 9l6 6 6-6" />
		</svg>
	</button>

	{#if showDropdown}
		<div class="lang-dropdown">
			<button class="lang-option" class:active={$locale === 'en'} onclick={() => setLocale('en')}>
				<span class="lang-flag">🇬🇧</span>
				English
			</button>
			<button class="lang-option" class:active={$locale === 'de'} onclick={() => setLocale('de')}>
				<span class="lang-flag">🇩🇪</span>
				Deutsch
			</button>
		</div>
	{/if}
</div>

<svelte:window
	onclick={(e) => {
		const target = e.target as HTMLElement;
		if (!target.closest('.lang-switcher')) {
			showDropdown = false;
		}
	}}
/>

<style>
	.lang-switcher {
		position: relative;
	}

	.lang-btn {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.75rem;
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-full);
		color: var(--text-secondary);
		cursor: pointer;
		transition: all var(--transition-base);
		font-family: inherit;
		font-size: 0.8125rem;
		font-weight: 500;
	}

	.lang-btn:hover {
		background: var(--bg-card-hover);
		border-color: var(--accent-primary);
		color: var(--text-primary);
	}

	.lang-code {
		min-width: 20px;
		text-align: center;
	}

	.lang-dropdown {
		position: absolute;
		top: calc(100% + 0.5rem);
		right: 0;
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		padding: 0.5rem;
		min-width: 140px;
		box-shadow: var(--shadow-xl);
		z-index: 200;
		animation: fadeIn 0.15s ease;
	}

	.lang-option {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		width: 100%;
		padding: 0.625rem 0.75rem;
		border: none;
		background: none;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		border-radius: var(--radius-sm);
		cursor: pointer;
		transition: all var(--transition-fast);
		font-family: inherit;
		text-align: left;
	}

	.lang-option:hover {
		background: var(--bg-card-hover);
		color: var(--text-primary);
	}

	.lang-option.active {
		background: rgba(99, 102, 241, 0.1);
		color: var(--accent-primary);
	}

	.lang-flag {
		font-size: 1rem;
	}
</style>
