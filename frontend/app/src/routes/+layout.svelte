<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import faviconDark from '$lib/assets/favicon-dark.svg';
	import { themeStore, CVD_PALETTES, THEME_PALETTES } from '$lib/stores/theme';
	import { privacyStore } from '$lib/stores/privacy';
	import { onMount } from 'svelte';
	import { dev } from '$app/environment';
	import ConsentModal from '$lib/components/ConsentModal.svelte';

	let { children } = $props();

	let doDataAnalysis = $derived(!dev && $privacyStore.analyticsAccepted);

	let showConsentModal = $state(false);
	let initialized = $state(false);
	onMount(() => {
		const stored = localStorage.getItem('privacy-settings');
		if (stored) {
			const settings = JSON.parse(stored);
			showConsentModal = !dev && !settings.hidden && settings.analyticsAccepted !== true;
		} else {
			showConsentModal = !dev;
		}
		initialized = true;
	});

	$effect(() => {
		if (initialized) {
			showConsentModal = !dev && !$privacyStore.hidden && $privacyStore.analyticsAccepted !== true;
		}
	});

	function applyThemeVariables(override: keyof typeof CVD_PALETTES) {
		if (typeof document === 'undefined') return;

		const globalTheme = $themeStore.globalTheme;
		const basePalette = THEME_PALETTES[globalTheme];
		const cvdPalette = CVD_PALETTES[override];
		const root = document.documentElement;

		root.style.setProperty('--bg-primary', basePalette.bgPrimary);
		root.style.setProperty('--bg-secondary', basePalette.bgSecondary);
		root.style.setProperty('--bg-card', basePalette.bgCard);
		root.style.setProperty('--bg-card-hover', basePalette.bgCardHover);
		root.style.setProperty('--bg-elevated', basePalette.bgElevated);
		root.style.setProperty('--text-primary', basePalette.textPrimary);
		root.style.setProperty('--text-secondary', basePalette.textSecondary);
		root.style.setProperty('--text-muted', basePalette.textMuted);

		const accentSource = cvdPalette || basePalette;
		root.style.setProperty('--accent-primary', accentSource.accentPrimary);
		root.style.setProperty('--accent-secondary', accentSource.accentSecondary);
		root.style.setProperty('--accent-gradient', accentSource.accentGradient);
		root.style.setProperty('--success', accentSource.success);
		root.style.setProperty('--error', accentSource.error);
		root.style.setProperty('--warning', accentSource.warning);

		if (globalTheme === 'light-modern') {
			document.body.classList.add('light-theme');
		} else {
			document.body.classList.remove('light-theme');
		}
	}

	onMount(() => {
		const stored = localStorage.getItem('theme-settings');
		let override: keyof typeof CVD_PALETTES = 'none';
		if (stored) {
			try {
				const settings = JSON.parse(stored);
				override = settings.colorBlindOverride || 'none';
			} catch {
				override = 'none';
			}
		}
		applyThemeVariables(override);
	});

	$effect(() => {
		applyThemeVariables($themeStore.colorBlindOverride);
	});
</script>

<svelte:head>
	{#if doDataAnalysis}
		<script
			defer
			src="https://analytics.tanker24.eu/script.js"
			data-website-id="66a25fa7-5924-4ea9-99c6-0f00dfc01f1d"
			integrity="p2xthgMxVFd6Ks4b7KkPf3VhCB7+yQn9QOpw1PpxKBItrVvsF8DwU/fUgUp4NnjR"
			crossorigin=""
		></script>
	{/if}
	<link rel="icon" href={$themeStore.globalTheme === 'dark-modern' ? faviconDark : favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
	<title>Tanker24</title>
</svelte:head>

{@render children()}

{#if showConsentModal}
	<ConsentModal />
{/if}
