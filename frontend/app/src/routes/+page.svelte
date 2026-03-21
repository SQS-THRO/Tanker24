<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/button.svelte';
	import { authService } from '$lib/services/api';
	import { resolve } from '$app/paths';

	let user = $state<{ forename: string } | null>(null);
	let showDropdown = $state(false);

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (token) {
			try {
				const userData = await authService.getCurrentUser(token);
				user = userData;
			} catch {
				localStorage.removeItem('token');
			}
		}
	});

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	async function logout() {
		await authService.logout();
		localStorage.removeItem('token');
		user = null;
		showDropdown = false;
	}

	function handleWindowClick(e: MouseEvent) {
		const target = e.target as HTMLElement;
		if (!target.closest('.profile-wrapper')) {
			showDropdown = false;
		}
	}
</script>

<svelte:window onclick={handleWindowClick} />

<main>
	<!-- HERO -->
	<section class="hero">
		<h1>Fill your Gas cheaper with Tanker24</h1>
		<p>The modern way to fill you Gas</p>
		<Button label="Go to Map" href="/map" />
	</section>

	{#if user}
		<div class="profile-wrapper">
			<button class="profile-btn" onclick={toggleDropdown}>
				{user.forename}
			</button>
			{#if showDropdown}
				<div class="dropdown">
					<button class="dropdown-item" onclick={logout}>Logout</button>
				</div>
			{/if}
		</div>
	{:else}
		<div class="profile-wrapper">
			<a href={resolve('/login')} class="profile-btn login-btn" aria-label="Login">
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
		</div>
	{/if}

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

	.profile-wrapper {
		position: absolute;
		top: 1rem;
		right: 1rem;
	}

	.profile-btn {
		width: auto;
		min-width: 48px;
		height: 48px;
		padding: 0 16px;
		border-radius: 24px;
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
		font-weight: 500;
		font-size: 1rem;
		font-family: inherit;
		border: none;
		cursor: pointer;
	}

	.profile-btn:hover {
		transform: scale(1.1);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
	}

	.dropdown {
		position: absolute;
		top: 100%;
		right: 0;
		margin-top: 8px;
		background: white;
		border-radius: 8px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
		overflow: hidden;
		min-width: 120px;
	}

	.dropdown-item {
		width: 100%;
		padding: 12px 16px;
		border: none;
		background: none;
		text-align: left;
		cursor: pointer;
		font-size: 1rem;
		color: #111;
		transition: background 0.2s ease;
	}

	.dropdown-item:hover {
		background: #f5f5f5;
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
