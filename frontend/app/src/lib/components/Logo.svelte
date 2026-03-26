<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

	const { size = 32 } = $props<{
		size?: number;
	}>();
</script>

<img src={favicon} alt="Tanker24" width={size} height={size} class="logo-icon" />

<style>
	.logo-icon {
		border-radius: 6px;
		flex-shrink: 0;
	}
</style>
