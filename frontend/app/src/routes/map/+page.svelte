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

		L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
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
		<a href={resolve('/')} class="logo">
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
				<div class="user-menu-wrapper">
					<button class="user-btn" onclick={() => (showUserMenu = !showUserMenu)}>
						<span class="user-avatar">
							{user.forename[0]}{user.surname?.[0] || ''}
						</span>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M6 9l6 6 6-6" />
						</svg>
					</button>
					{#if showUserMenu}
						<div class="user-dropdown">
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
		if (!target.closest('.user-menu-wrapper')) {
			showUserMenu = false;
		}
	}}
/>

<style>
	main {
		position: relative;
		height: 100vh;
		width: 100vw;
		overflow: hidden;
	}

	.map-header {
		position: absolute;
		top: 1rem;
		left: 1rem;
		right: 1rem;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.75rem 1rem;
		border-radius: var(--radius-lg);
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.625rem;
		text-decoration: none;
		color: var(--text-primary);
		font-weight: 700;
		font-size: 1rem;
		flex-shrink: 0;
	}

	.logo span {
		display: none;
	}

	@media (min-width: 640px) {
		.logo span {
			display: inline;
		}
	}

	.header-center {
		flex: 1;
		max-width: 400px;
	}

	.search-box {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-full);
		padding: 0.5rem 1rem;
		transition: all var(--transition-fast);
	}

	.search-box:focus-within {
		border-color: var(--accent-primary);
		box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
	}

	.search-box svg {
		color: var(--text-muted);
		flex-shrink: 0;
	}

	.search-input {
		flex: 1;
		background: none;
		border: none;
		color: var(--text-primary);
		font-size: 0.875rem;
		outline: none;
	}

	.search-input::placeholder {
		color: var(--text-muted);
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-shrink: 0;
	}

	.user-menu-wrapper {
		position: relative;
	}

	.user-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.375rem 0.625rem 0.375rem 0.375rem;
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-full);
		color: var(--text-primary);
		cursor: pointer;
		transition: all var(--transition-base);
		font-family: inherit;
	}

	.user-btn:hover {
		background: var(--bg-card-hover);
		border-color: var(--accent-primary);
	}

	.user-avatar {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: var(--accent-gradient);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.user-dropdown {
		position: absolute;
		top: calc(100% + 0.5rem);
		right: 0;
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		padding: 0.5rem;
		min-width: 180px;
		box-shadow: var(--shadow-xl);
		animation: fadeIn 0.15s ease;
	}

	.dropdown-header {
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid var(--border-subtle);
		margin-bottom: 0.25rem;
	}

	.dropdown-name {
		font-size: 0.875rem;
		font-weight: 600;
	}

	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		width: 100%;
		padding: 0.625rem 0.75rem;
		border: none;
		background: none;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		border-radius: var(--radius-sm);
		cursor: pointer;
		transition: all var(--transition-fast);
		text-decoration: none;
		font-family: inherit;
	}

	.dropdown-item:hover {
		background: var(--bg-card-hover);
		color: var(--text-primary);
	}

	.dropdown-item.logout:hover {
		background: rgba(239, 68, 68, 0.1);
		color: var(--error);
	}

	.error-banner {
		position: absolute;
		top: 5rem;
		left: 50%;
		transform: translateX(-50%);
		z-index: 999;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1.25rem;
		background: rgba(239, 68, 68, 0.15);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: var(--radius-md);
		color: #fca5a5;
		font-size: 0.875rem;
		backdrop-filter: blur(10px);
	}

	.map-container {
		height: 100%;
		width: 100%;
	}

	.map-controls {
		position: absolute;
		bottom: 1.5rem;
		left: 1rem;
		z-index: 1000;
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 0.75rem 1rem;
		border-radius: var(--radius-md);
	}

	.station-count {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
	}

	.btn-sm {
		padding: 0.5rem 1rem;
		font-size: 0.8125rem;
	}

	.location-btn {
		position: absolute;
		bottom: 1.5rem;
		right: 1rem;
		z-index: 1000;
		width: 44px;
		height: 44px;
		border-radius: var(--radius-md);
		border: none;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		color: var(--accent-primary);
		transition: all var(--transition-base);
	}

	.location-btn:hover {
		color: var(--accent-secondary);
		transform: scale(1.05);
	}

	:global(.user-marker) {
		background: transparent !important;
		border: none !important;
	}

	:global(.user-marker-inner) {
		position: relative;
		width: 24px;
		height: 24px;
	}

	:global(.user-marker-pulse) {
		position: absolute;
		inset: 0;
		border-radius: 50%;
		background: rgba(59, 130, 246, 0.3);
		animation: userPulse 2s ease-out infinite;
	}

	:global(.user-marker-dot) {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: #3b82f6;
		border: 3px solid white;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}

	@keyframes userPulse {
		0% {
			transform: scale(1);
			opacity: 1;
		}
		100% {
			transform: scale(2.5);
			opacity: 0;
		}
	}

	:global(.station-marker) {
		background: transparent !important;
		border: none !important;
	}

	:global(.station-marker-inner) {
		width: 40px;
		height: 40px;
		background: var(--bg-card);
		border: 2px solid var(--accent-primary);
		border-radius: var(--radius-md);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--accent-primary);
		box-shadow: var(--shadow-lg);
		transition: all var(--transition-base);
	}

	:global(.station-marker:hover .station-marker-inner) {
		background: var(--accent-primary);
		color: white;
		transform: scale(1.1);
	}

	:global(.leaflet-popup-content-wrapper) {
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-xl);
	}

	:global(.leaflet-popup-content) {
		margin: 0.75rem 1rem;
		color: var(--text-primary);
		font-family: var(--font-sans);
	}

	:global(.leaflet-popup-tip) {
		background: var(--bg-card);
		border: 1px solid var(--border-light);
	}

	:global(.popup h4) {
		font-size: 0.9375rem;
		font-weight: 600;
		margin-bottom: 0.25rem;
	}

	:global(.popup p) {
		font-size: 0.8125rem;
		color: var(--text-secondary);
	}

	:global(.leaflet-control-attribution) {
		background: rgba(10, 10, 11, 0.8) !important;
		color: var(--text-muted) !important;
		font-size: 0.625rem !important;
		backdrop-filter: blur(10px);
	}

	:global(.leaflet-control-attribution a) {
		color: var(--accent-secondary) !important;
	}
</style>
