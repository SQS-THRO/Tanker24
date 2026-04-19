<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import faviconDark from '$lib/assets/favicon-dark.svg';
	import { themeStore } from '$lib/stores/theme';

	const { size = 32 } = $props<{
		size?: number;
	}>();
</script>

<img src={$themeStore.globalTheme === 'dark-modern' ? faviconDark : favicon} alt="Tanker24" width={size} height={size} class="logo-icon" />
