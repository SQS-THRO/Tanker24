<script lang="ts">
	import { resolve } from '$app/paths';
	import Button from '$lib/components/button.svelte';
</script>

<main>
	<!-- HERO -->
	<section class="hero">
		<h1>Fill your Gas cheaper with Tanker24</h1>
		<p>The modern way to fill you Gas</p>
		<Button label="Go to Map" href="/map" />
	</section>

	<a href={resolve('/login')} class="profile-btn" aria-label="Login">
		<svg
			xmlns="http://www.w3.org/2000/svg"
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			stroke-linecap="round"
			stroke-linejoin="round"
		>
			<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
			<circle cx="12" cy="7" r="4" />
		</svg>
	</a>

	<!-- FEATURES -->
	<section class="features">
		<div class="card">
			<h3>⚡ Fast</h3>
		</div>
		<div class="card">
			<h3>🧩 Simple</h3>
		</div>
		<div class="card">
			<h3>🚀 Powerful</h3>
		</div>
	</section>
</main>

<style>
	main {
		font-family: system-ui, sans-serif;
		text-align: center;
		position: relative;
	}

	section {
		padding: 4rem 2rem;
	}

	.profile-btn {
		position: absolute;
		top: 1rem;
		right: 1rem;
		width: 48px;
		height: 48px;
		border-radius: 50%;
		background: white;
		color: #111;
		display: flex;
		align-items: center;
		justify-content: center;
		text-decoration: none;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease;
	}

	.profile-btn:hover {
		transform: scale(1.1);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
	}

	.hero {
		background: #111;
		color: white;
	}

	.hero h1 {
		font-size: 3rem;
		margin-bottom: 1rem;
	}

	.features {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.card {
		background: #f5f5f5;
		padding: 1.5rem;
		border-radius: 10px;
		width: 200px;
	}
</style>
