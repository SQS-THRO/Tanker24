<script lang="ts">
	import Button from '$lib/components/button.svelte';
</script>

<main>
	<section class="hero">
		<div class="card">
			<h3>MAP</h3>
			<Button label="Back to Landing Page" href="/" />
		</div>
	</section>
</main>

<style>
	main {
		font-family: system-ui, sans-serif;
		text-align: center;
	}

	section {
		padding: 4rem 2rem;
	}

	.hero {
		background: #111;
		color: white;
	}
</style>
