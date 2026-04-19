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
				<img class="lang-flag" src="https://twemoji.maxcdn.com/v/latest/svg/1f1ec-1f1e7.svg" alt="🇬🇧" />
				English
			</button>
			<button class="lang-option" class:active={$locale === 'de'} onclick={() => setLocale('de')}>
				<img class="lang-flag" src="https://twemoji.maxcdn.com/v/latest/svg/1f1e9-1f1ea.svg" alt="🇩🇪" />
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
