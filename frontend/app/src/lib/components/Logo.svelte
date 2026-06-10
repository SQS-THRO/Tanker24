<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import faviconDark from '$lib/assets/favicon-dark.svg';
	import { themeStore } from '$lib/stores/theme';

	const { size = 32 } = $props<{
		size?: number;
	}>();

	let prefersDark = $state(false);

	$effect(() => {
		if (typeof window === 'undefined') return;
		const mq = window.matchMedia('(prefers-color-scheme: dark)');
		prefersDark = mq.matches;
		const handler = () => { prefersDark = mq.matches; };
		mq.addEventListener('change', handler);
		return () => mq.removeEventListener('change', handler);
	});

	const isDark = $derived(
		$themeStore.globalTheme === 'dark-modern' ||
		($themeStore.globalTheme === 'auto' && prefersDark)
	);
</script>

<img src={isDark ? faviconDark : favicon} alt="Tanker24" width={size} height={size} class="logo-icon" />
