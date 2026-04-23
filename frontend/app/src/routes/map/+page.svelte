<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { resolve } from '$app/paths';
	import { stationService, type Station } from '$lib/services/stations_api';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import AuthRequiredModal from '$lib/components/AuthRequiredModal.svelte';
	import { t } from '$lib/stores/locale';
	import { themeStore } from '$lib/stores/theme';
	import type { Map } from 'leaflet';

	const DEFAULT_LAT = 47.79;
	const DEFAULT_LNG = 12.1;
	const DEFAULT_ZOOM = 11;

	let mapContainer: HTMLDivElement;
	let stations: Station[] = $state([]);
	let error = $state('');
	let userLat = $state<number | null>(null);
	let userLng = $state<number | null>(null);
	let user = $state<{ forename: string; surname?: string } | null>(null);
	let showUserMenu = $state(false);
	let showAuthModal = $state(false);
	let map: Map | null = null;

	function getUserLocation(): Promise<{ lat: number; lng: number }> {
		return new Promise((resolve) => {
			if (!navigator.geolocation) {
				resolve({ lat: DEFAULT_LAT, lng: DEFAULT_LNG });
				return;
			}

			navigator.geolocation.getCurrentPosition(
				(position) => {
					resolve({
						lat: position.coords.latitude,
						lng: position.coords.longitude
					});
				},
				() => {
					resolve({ lat: DEFAULT_LAT, lng: DEFAULT_LNG });
				},
				{ timeout: 5000 }
			);
		});
	}

	async function loadUser() {
		const token = localStorage.getItem('token');
		if (token) {
			try {
				user = await authService.getCurrentUser(token);
			} catch {
				user = null;
			}
		}
	}

	async function logout() {
		await authService.logout();
		localStorage.removeItem('token');
		user = null;
		showUserMenu = false;
		await goto(resolve('/'));
	}

	onMount(async () => {
		if (!browser) return;

		const token = localStorage.getItem('token');
		if (!token) {
			showAuthModal = true;
			return;
		}

		await loadUser();

		try {
			stations = await stationService.getStations(token);
		} catch {
			error = $t.map.loginRequired;
		}

		const { lat, lng } = await getUserLocation();
		userLat = lat;
		userLng = lng;

		const L = (await import('leaflet')).default;

		map = L.map(mapContainer).setView([lat, lng], DEFAULT_ZOOM);

		const isDarkTheme = $themeStore.globalTheme === 'dark-modern';
		const tileUrl = isDarkTheme ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
		const fallbackUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

		L.tileLayer(tileUrl, {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			errorTileUrl: fallbackUrl
		}).addTo(map);

		if (userLat !== null && userLng !== null) {
			const userIcon = L.divIcon({
				className: 'user-marker',
				html: `
					<div class="user-marker-inner">
						<div class="user-marker-pulse"></div>
						<div class="user-marker-dot"></div>
					</div>
				`,
				iconSize: [24, 24],
				iconAnchor: [12, 12]
			});
			L.marker([userLat, userLng], { icon: userIcon }).addTo(map).bindPopup(`<div class="popup user-popup"><strong>${$t.map.yourLocation}</strong></div>`).openPopup();
		}

		stations.forEach((station) => {
			if (station.latitude !== null && station.longitude !== null) {
				const stationIcon = L.divIcon({
					className: 'station-marker',
					html: `
						<div class="station-marker-inner">
							<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M3 22V8l9-6 9 6v14H3z" />
								<path d="M9 22V12h6v10" />
							</svg>
						</div>
					`,
					iconSize: [40, 40],
					iconAnchor: [20, 40],
					popupAnchor: [0, -40]
				});
				const popupContent = `
					<div class="popup station-popup">
						<h4>${station.name}</h4>
						${station.description ? `<p>${station.description}</p>` : ''}
					</div>
				`;
				L.marker([station.latitude, station.longitude], { icon: stationIcon }).addTo(map).bindPopup(popupContent);
			}
		});
	});
</script>

<main>
	<AuthRequiredModal show={showAuthModal} />
	<div class="map-header glass">
		<a href={resolve('/')} class="navbar-logo">
			<Logo size={28} />
			<span>Tanker24</span>
		</a>

		<div class="header-center">
			<div class="search-box">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="11" cy="11" r="8" />
					<path d="M21 21l-4.35-4.35" />
				</svg>
				<input type="text" placeholder={$t.map.searchPlaceholder} class="search-input" />
			</div>
		</div>

		<div class="header-actions">
			<LanguageSwitcher />
			{#if user}
				<div class="profile-wrapper">
					<button class="user-btn" onclick={() => (showUserMenu = !showUserMenu)}>
						<span class="user-avatar">
							{user.forename[0]}{user.surname?.[0] || ''}
						</span>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M6 9l6 6 6-6" />
						</svg>
					</button>
					{#if showUserMenu}
						<div class="dropdown">
							<div class="dropdown-header">
								<span class="dropdown-name">{user.forename} {user.surname || ''}</span>
							</div>
							<a href={resolve('/account')} class="dropdown-item">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
									<circle cx="12" cy="7" r="4" />
								</svg>
								{$t.nav.account}
							</a>
							<button class="dropdown-item logout" onclick={logout}>
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
									<polyline points="16,17 21,12 16,7" />
									<line x1="21" y1="12" x2="9" y2="12" />
								</svg>
								{$t.nav.logout}
							</button>
						</div>
					{/if}
				</div>
			{:else}
				<a href={resolve('/login')} class="btn btn-secondary">{$t.nav.signIn}</a>
			{/if}
		</div>
	</div>

	{#if error}
		<div class="error-banner">
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<circle cx="12" cy="12" r="10" />
				<line x1="12" y1="8" x2="12" y2="12" />
				<line x1="12" y1="16" x2="12.01" y2="16" />
			</svg>
			{error}
			<a href={resolve('/login')} class="btn btn-sm">{$t.map.login}</a>
		</div>
	{/if}

	<div class="map-container" bind:this={mapContainer}></div>

	<div class="map-controls glass">
		<div class="station-count">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M3 22V8l9-6 9 6v14H3z" />
				<path d="M9 22V12h6v10" />
			</svg>
			<span>{stations.length} {$t.map.stations}</span>
		</div>
		<a href={resolve('/')} class="btn btn-secondary btn-sm">
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M19 12H5M12 19l-7-7 7-7" />
			</svg>
			{$t.map.back}
		</a>
	</div>

	{#if userLat !== null && userLng !== null}
		<button
			class="location-btn glass"
			onclick={() => {
				if (map) {
					map.setView([userLat!, userLng!], DEFAULT_ZOOM);
				}
			}}
			aria-label="Go to my location"
		>
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<circle cx="12" cy="12" r="3" />
				<path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
			</svg>
		</button>
	{/if}
</main>

<svelte:window
	onclick={(e) => {
		const target = e.target as HTMLElement;
		if (!target.closest('.profile-wrapper')) {
			showUserMenu = false;
		}
	}}
/>
