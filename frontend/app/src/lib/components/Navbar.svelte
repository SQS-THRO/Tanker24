<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import { t } from '$lib/stores/locale';
	import { themeStore, type GlobalTheme } from '$lib/stores/theme';

	interface Props {
		showMapLink?: boolean;
		showAuthButtons?: boolean;
	}

	let { showMapLink = true, showAuthButtons = true }: Props = $props();

	let showDropdown = $state(false);
	let scrolled = $state(false);

	onMount(() => {
		auth.checkAuth();

		scrolled = window.scrollY > 50;
		const handleScroll = () => {
			scrolled = window.scrollY > 50;
		};
		window.addEventListener('scroll', handleScroll);
	});

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	async function logout() {
		await auth.logout();
		showDropdown = false;
		goto(resolve('/'));
	}

	function handleWindowClick(e: MouseEvent) {
		const target = e.target as HTMLElement;
		if (!target.closest('.profile-wrapper')) {
			showDropdown = false;
		}
	}

	const cycleOrder: GlobalTheme[] = ['dark-modern', 'light-modern', 'auto'];

	function cycleTheme() {
		const current = $themeStore.globalTheme;
		const nextIndex = (cycleOrder.indexOf(current) + 1) % cycleOrder.length;
		themeStore.setGlobalTheme(cycleOrder[nextIndex]);
	}
</script>

<svelte:window onclick={handleWindowClick} />

<nav class="navbar" class:scrolled>
	<div class="navbar-inner">
		<a href={resolve('/')} class="navbar-logo header-logo">
			<Logo size={32} />
			<span>Tanker24</span>
		</a>

		<div class="nav-actions">
			<LanguageSwitcher />
			<button class="theme-toggle header-theme-toggle" onclick={cycleTheme} aria-label="Toggle theme">
				{#if $themeStore.globalTheme === 'dark-modern'}
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
					</svg>
				{:else if $themeStore.globalTheme === 'light-modern'}
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="5" />
						<line x1="12" y1="1" x2="12" y2="3" />
						<line x1="12" y1="21" x2="12" y2="23" />
						<line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
						<line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
						<line x1="1" y1="12" x2="3" y2="12" />
						<line x1="21" y1="12" x2="23" y2="12" />
						<line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
						<line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
					</svg>
				{:else}
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="12" cy="12" r="9" />
						<path d="M8 17l4-10 4 10" />
						<path d="M10 13h4" />
					</svg>
				{/if}
			</button>
			{#if showMapLink}
				<a href={resolve('/map')} class="btn btn-secondary nav-link">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
						<line x1="9" y1="3" x2="9" y2="18" />
						<line x1="15" y1="6" x2="15" y2="21" />
					</svg>
					{$t.nav.map}
				</a>
			{/if}
			{#if $auth.user}
				<div class="profile-wrapper header-profile">
					<button class="profile-btn" onclick={toggleDropdown}>
						<span class="avatar">
							{$auth.user.forename[0]}{$auth.user.surname?.[0] || ''}
						</span>
						<span class="username">{$auth.user.forename}</span>
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
