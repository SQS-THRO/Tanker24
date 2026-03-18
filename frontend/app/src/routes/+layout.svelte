<script lang="ts">
	import favicon from '../../../../docs/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Tanker24</title>
</svelte:head>

{@render children()}
