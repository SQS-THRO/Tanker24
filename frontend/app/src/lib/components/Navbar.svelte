<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { authService } from '$lib/services/auth_api';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import { t } from '$lib/stores/locale';

	interface Props {
		showMapLink?: boolean;
		showAuthButtons?: boolean;
	}

	let { showMapLink = true, showAuthButtons = true }: Props = $props();

	let user = $state<{ forename: string; surname?: string } | null>(null);
	let showDropdown = $state(false);
	let scrolled = $state(false);

	onMount(() => {
		const init = async () => {
			const token = localStorage.getItem('token');
			if (token) {
				try {
					const userData = await authService.getCurrentUser(token);
					user = userData;
				} catch {
					localStorage.removeItem('token');
				}
			}

			scrolled = window.scrollY > 50;
			const handleScroll = () => {
				scrolled = window.scrollY > 50;
			};
			window.addEventListener('scroll', handleScroll);
		};
		init();
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

<nav class="navbar" class:scrolled>
	<div class="navbar-inner">
		<a href={resolve('/')} class="navbar-logo">
			<Logo size={32} />
			<span>Tanker24</span>
		</a>

		<div class="nav-actions">
			<LanguageSwitcher />
			{#if showMapLink}
				<a href={resolve('/map')} class="btn btn-ghost nav-link">{$t.nav.map}</a>
			{/if}
			{#if user}
				<div class="profile-wrapper">
					<button class="profile-btn" onclick={toggleDropdown}>
						<span class="avatar">
							{user.forename[0]}{user.surname?.[0] || ''}
						</span>
						<span class="username">{user.forename}</span>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M6 9l6 6 6-6" />
						</svg>
					</button>
					{#if showDropdown}
						<div class="dropdown">
							<a href={resolve('/account')} class="dropdown-item">
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
									<circle cx="12" cy="7" r="4" />
								</svg>
								{$t.nav.account}
							</a>
							<button class="dropdown-item logout" onclick={logout}>
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
									<polyline points="16,17 21,12 16,7" />
									<line x1="21" y1="12" x2="9" y2="12" />
								</svg>
								{$t.nav.logout}
							</button>
						</div>
					{/if}
				</div>
			{:else if showAuthButtons}
				<a href={resolve('/login')} class="btn btn-secondary">{$t.nav.signIn}</a>
				<a href={resolve('/register')} class="btn btn-primary">{$t.nav.getStarted}</a>
			{/if}
		</div>
	</div>
</nav>
