<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { resolve } from '$app/paths';
	import { stationService, type Station, type TankerkoenigStation } from '$lib/services/stations_api';
	import { auth } from '$lib/stores/auth';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import AuthRequiredModal from '$lib/components/AuthRequiredModal.svelte';
	import { t, locale } from '$lib/stores/locale';
	import { themeStore, type GlobalTheme } from '$lib/stores/theme';
	import { fuelType, fuelTypeLabel, type FuelType } from '$lib/stores/fuelType';
	import type { Map, LayerGroup, Marker } from 'leaflet';
	import gasStationIcon from '$lib/assets/gasstation-icons/gasstation.svg?url';
	import gasStationDarkIcon from '$lib/assets/gasstation-icons/gasstation-dark.svg?url';

	const DEFAULT_LAT = 47.79;
	const DEFAULT_LNG = 12.1;
	const DEFAULT_ZOOM = 11;
	const NEARBY_DEBOUNCE_MS = 1500;

	let L: typeof import('leaflet').default;

	let mapContainer: HTMLDivElement;
	let stations: Station[] = $state([]);
	let nearbyStations: TankerkoenigStation[] = $state([]);
	let sortedNearbyStations: TankerkoenigStation[] = $state([]);
	let minSelectedFuelPrice: number | null = $state(null);

	function sortStations(fuel: FuelType) {
		sortedNearbyStations = [...nearbyStations].sort((a, b) => {
			const pA = a[fuel];
			const pB = b[fuel];
			if (pA === null && pB === null) return 0;
			if (pA === null) return 1;
			if (pB === null) return -1;
			return pA - pB;
		});
	}
	let knownStations = new Map<string, TankerkoenigStation>();
	let error = $state('');
	let nearbyFetchError = $state('');
	let searchQuery = $state('');
	let userLat = $state<number | null>(null);
	let userLng = $state<number | null>(null);
	let user = $state<{ forename: string; surname?: string } | null>(null);
	let showUserMenu = $state(false);
	let showAuthModal = $state(false);
	let map: Map | null = null;
	let tileLayer: ReturnType<L['tileLayer']> | null = null;
	let userLocationMarker: Marker | null = null;
	let userLayerGroup: LayerGroup | null = null;
	let nearbyLayerGroup: LayerGroup | null = null;
	let moveDebounceTimer: ReturnType<typeof setTimeout> | null = null;
	let isNearbyLoading = $state(false);
	let showFuelDropdown = $state(false);
	let sidebarOpen = $state(false);
	let manuallyClosed = false;
	let nearbyMarkersMap = new Map<string, Marker>();

	const fuelTypes: FuelType[] = ['diesel', 'e5', 'e10'];

	function debounce(fn: () => void, ms: number) {
		if (moveDebounceTimer) clearTimeout(moveDebounceTimer);
		moveDebounceTimer = setTimeout(() => {
			moveDebounceTimer = null;
			fn();
		}, ms);
	}

	function isDarkTheme(): boolean {
		const theme = $themeStore.globalTheme;
		if (theme === 'auto') {
			if (typeof window === 'undefined') return true;
			return window.matchMedia('(prefers-color-scheme: dark)').matches;
		}
		return theme === 'dark-modern';
	}

	function getStationIconUrl() {
		return isDarkTheme() ? gasStationDarkIcon : gasStationIcon;
	}

	function refreshAllMarkers() {
		if (!map) return;

		// Refresh nearby stations
		if (nearbyLayerGroup) {
			nearbyLayerGroup.clearLayers();
			const center = map.getCenter();
			fetchNearbyStations(center.lat, center.lng);
		}

		// Refresh user's saved stations
		if (userLayerGroup && stations.length > 0) {
			userLayerGroup.clearLayers();
			const iconUrl = getStationIconUrl();
			stations.forEach((station) => {
				if (station.latitude !== null && station.longitude !== null) {
					const stationIcon = L.divIcon({
						className: 'station-marker',
						html: `
							<div class="station-marker-inner">
								<img src="${iconUrl}" alt="Station" width="24" height="24" />
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
					L.marker([station.latitude, station.longitude], { icon: stationIcon }).bindPopup(popupContent).addTo(userLayerGroup!);
				}
			});
		}
	}

	function refreshPopups() {
		if (!map || !L) return;

		if (userLocationMarker && userLat !== null && userLng !== null) {
			userLocationMarker.setPopupContent(`<div class="popup user-popup"><strong>${$t.map.yourLocation}</strong></div>`);
		}

		if (userLayerGroup && stations.length > 0) {
			userLayerGroup.clearLayers();
			const iconUrl = getStationIconUrl();
			stations.forEach((station) => {
				if (station.latitude !== null && station.longitude !== null) {
					const stationIcon = L.divIcon({
						className: 'station-marker',
						html: `
							<div class="station-marker-inner">
								<img src="${iconUrl}" alt="Station" width="24" height="24" />
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
					L.marker([station.latitude, station.longitude], { icon: stationIcon }).bindPopup(popupContent).addTo(userLayerGroup!);
				}
			});
		}

		updateNearbyMarkers();
	}

	function zoomIn() {
		if (map) map.zoomIn();
	}

	function zoomOut() {
		if (map) map.zoomOut();
	}

	function getTileUrl(isDark: boolean) {
		return isDark ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
	}

	function swapTileLayer(isDark: boolean) {
		if (!map || !tileLayer || !L) return;
		map.removeLayer(tileLayer);
		const url = getTileUrl(isDark);
		tileLayer = L.tileLayer(url, {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			errorTileUrl: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
		}).addTo(map);
	}
	
	function closeSidebar() {
		manuallyClosed = true;
		sidebarOpen = false;
	}

	function openSidebar() {
		manuallyClosed = false;
		sidebarOpen = true;
	}

	let themeInitialized = false;
	$effect(() => {
		void $themeStore.globalTheme;
		if (!themeInitialized) {
			themeInitialized = true;
			return;
		}
		swapTileLayer(isDarkTheme());
		refreshAllMarkers();
	});

	$effect(() => {
		if (typeof window === 'undefined') return;
		if ($themeStore.globalTheme === 'auto') {
			const mq = window.matchMedia('(prefers-color-scheme: dark)');
			const handler = () => {
				swapTileLayer(isDarkTheme());
				refreshAllMarkers();
			};
			mq.addEventListener('change', handler);
			return () => mq.removeEventListener('change', handler);
		}
	});

	let localeInitialized = false;
	$effect(() => {
		void $locale;
		if (!localeInitialized) {
			localeInitialized = true;
			return;
		}
		refreshPopups();
	});

	$effect(() => {
		const fuel = $fuelType;
		sortStations(fuel);
		const prices = nearbyStations.map((s) => s[fuel]).filter((v): v is number => v !== null && v !== undefined);
		minSelectedFuelPrice = prices.length > 0 ? Math.min(...prices) : null;
		if (nearbyLayerGroup && nearbyStations.length > 0) {
			updateNearbyMarkers();
		}
	});

	$effect(() => {
		if (nearbyStations.length >= 1 && manuallyClosed === false) {
			sidebarOpen = true;
		}
	});

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

	async function fetchNearbyStations(lat: number, lng: number) {
		const token = localStorage.getItem('token');
		if (!token || !map) return;

		isNearbyLoading = true;
		nearbyFetchError = '';

		try {
			const fresh = await stationService.getNearbyStations(lat, lng, token);
			for (const station of fresh) {
				knownStations.set(station.tankerkoenig_id, station);
			}
			nearbyStations = Array.from(knownStations.values());
			sortStations($fuelType);
		} catch {
			nearbyFetchError = $t.map.nearbyFetchFailed;
		} finally {
			isNearbyLoading = false;
		}

		updateNearbyMarkers();
	}

	function focusStation(station: TankerkoenigStation) {
		if (!map) return;
		map.setView([station.latitude, station.longitude], 15, { animate: true });
		const marker = nearbyMarkersMap.get(station.tankerkoenig_id);
		if (marker) {
			setTimeout(() => marker.openPopup(), 400);
		}
	}

	function updateNearbyMarkers() {
		if (!nearbyLayerGroup || !map || !L) return;

		nearbyLayerGroup.clearLayers();
		nearbyMarkersMap.clear();

		const selectedFuel = $fuelType;

		const fuelValues = nearbyStations.map((s) => s[selectedFuel]).filter((v): v is number => v !== null && v !== undefined);
		const minSelectedFuelPrice = fuelValues.length > 0 ? Math.min(...fuelValues) : null;

		nearbyStations.forEach((station) => {
			const prices = [
				{ type: 'diesel', value: station.diesel },
				{ type: 'e5', value: station.e5 },
				{ type: 'e10', value: station.e10 }
			].filter((p) => p.value !== null && p.value !== undefined);

			const addressParts = [station.street, station.house_number, station.post_code, station.place].filter(Boolean);
			const address = addressParts.join(', ');
			const priceRows = prices
				.map((p) => {
					const isSelectedFuel = p.type === selectedFuel;
					const isCheapest = isSelectedFuel && p.value === minSelectedFuelPrice && minSelectedFuelPrice !== null;
					const integer = Math.trunc(p.value as number);
					const dec = (p.value as number).toFixed(3).split('.')[1];
					const priceDisplay = p.value !== null ? `${integer}${$t.map.priceDevider}${dec}€` : '—';
					const classes = ['price-item'];
					if (isSelectedFuel) classes.push('selected-fuel');
					if (isCheapest) classes.push('cheapest');
					return `
					<div class="${classes.join(' ')}">
						<div class="fuel-label">${p.type.toUpperCase()}</div>
						<div class="fuel-price">${priceDisplay}</div>
					</div>
				`;
				})
				.join('');

			const popupContent = `
				<div class="station-popup-card">
					<h4>${station.name}</h4>
					<div class="brand-label">${station.brand}</div>
					${address ? `<div class="station-address">${address}</div>` : ''}
					<div class="open-badge ${station.is_open ? 'open' : 'closed'}">
						${station.is_open ? '●' : '●'} ${station.is_open ? $t.map.open : $t.map.closed}
					</div>
					<div class="price-grid">
						${priceRows}
					</div>
					${
						userLat !== null && userLng !== null && station.latitude !== null && station.longitude !== null
							? `<div class="station-distance">
						<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
							<circle cx="12" cy="9" r="2.5"/>
						</svg>
						${(map.distance([station.latitude, station.longitude], [userLat, userLng]) / 1000).toFixed(1)} ${$t.map.kilometers}
					</div>`
							: ''
					}
				</div>
			`;

			const iconUrl = getStationIconUrl();
			const isCheapestStation = station[selectedFuel] !== null && station[selectedFuel] === minSelectedFuelPrice;

			const stationIcon = L.divIcon({
				className: 'nearby-station-marker',
				html: `
					<div class="nearby-station-marker-inner${isCheapestStation ? ' cheapest-marker' : ''}">
						<img src="${iconUrl}" alt="Station" width="24" height="24" />
					</div>
				`,
				iconSize: [40, 40],
				iconAnchor: [20, 20],
				popupAnchor: [0, -20]
			});

			const marker = L.marker([station.latitude, station.longitude], { icon: stationIcon }).bindPopup(popupContent).addTo(nearbyLayerGroup);
			nearbyMarkersMap.set(station.tankerkoenig_id, marker);
		});
	}

	async function handleMapSearch() {
		if (!map || !searchQuery.trim()) return;
		const center = map.getCenter();
		await fetchNearbyStations(center.lat, center.lng);
	}

	async function logout() {
		await auth.logout();
		user = null;
		showUserMenu = false;
		await goto(resolve('/'));
	}

	onMount(async () => {
		if (!browser) return;

		const leaflet = await import('leaflet');
		L = leaflet.default;

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

		map = L.map(mapContainer, { zoomControl: false }).setView([lat, lng], DEFAULT_ZOOM);

		userLayerGroup = L.layerGroup().addTo(map);
		nearbyLayerGroup = L.layerGroup().addTo(map);

		const fallbackUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

		tileLayer = L.tileLayer(getTileUrl(isDarkTheme()), {
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
			userLocationMarker = L.marker([userLat, userLng], { icon: userIcon }).addTo(map);
			userLocationMarker.bindPopup(`<div class="popup user-popup"><strong>${$t.map.yourLocation}</strong></div>`).openPopup();
		}

		// Create user's saved station markers
		if (userLayerGroup && stations.length > 0) {
			const iconUrl = getStationIconUrl();
			stations.forEach((station) => {
				if (station.latitude !== null && station.longitude !== null) {
					const stationIcon = L.divIcon({
						className: 'station-marker',
						html: `
							<div class="station-marker-inner">
								<img src="${iconUrl}" alt="Station" width="24" height="24" />
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
					L.marker([station.latitude, station.longitude], { icon: stationIcon }).bindPopup(popupContent).addTo(userLayerGroup!);
				}
			});
		}

		await fetchNearbyStations(lat, lng);

		map.on('moveend', () => {
			debounce(async () => {
				if (!map) return;
				const center = map.getCenter();
				await fetchNearbyStations(center.lat, center.lng);
			}, NEARBY_DEBOUNCE_MS);
		});
	});

	onDestroy(() => {
		if (moveDebounceTimer) clearTimeout(moveDebounceTimer);
		if (map) {
			map.off('moveend');
			map.remove();
		}
	});

	const cycleOrder: GlobalTheme[] = ['dark-modern', 'light-modern', 'auto'];

	function cycleTheme() {
		const current = $themeStore.globalTheme;
		const nextIndex = (cycleOrder.indexOf(current) + 1) % cycleOrder.length;
		themeStore.setGlobalTheme(cycleOrder[nextIndex]);
	}
</script>

<main>
	<AuthRequiredModal show={showAuthModal} />
	<div class="map-header glass">
		<button class="sidebar-toggle glass" onclick={() => openSidebar()} aria-label="Toggle station list">
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<line x1="3" y1="6" x2="21" y2="6" />
				<line x1="3" y1="12" x2="21" y2="12" />
				<line x1="3" y1="18" x2="21" y2="18" />
			</svg>
		</button>
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
				<input
					type="text"
					placeholder={$t.map.searchPlaceholder}
					class="search-input"
					bind:value={searchQuery}
					onkeydown={(e) => {
						if (e.key === 'Enter') {
							handleMapSearch();
						}
					}}
				/>
				{#if searchQuery}
					<button class="search-btn" onclick={handleMapSearch} aria-label="Search map center">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M5 12h14M12 5l7 7-7 7" />
						</svg>
					</button>
				{/if}
			</div>

			<div class="fuel-selector-wrapper">
				<button class="fuel-selector-btn glass" onclick={() => (showFuelDropdown = !showFuelDropdown)} aria-label={$t.map.selectFuel}>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M3 22V6a2 2 0 012-2h8a2 2 0 012 2v16" />
						<path d="M3 22h12" />
						<path d="M15 10l2.5-2.5a1.414 1.414 0 012 0l1 1a1.414 1.414 0 010 2L18 13" />
						<path d="M15 10v6a2 2 0 002 2h0a2 2 0 002-2v-2" />
					</svg>
					<span>{$fuelTypeLabel}</span>
					<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M6 9l6 6 6-6" />
					</svg>
				</button>
				{#if showFuelDropdown}
					<div class="fuel-dropdown glass">
						{#each fuelTypes as type (type)}
							<button
								class="fuel-dropdown-item"
								class:active={type === $fuelType}
								onclick={() => {
									fuelType.set(type);
									showFuelDropdown = false;
								}}
							>
								{type === 'diesel' ? $t.map.diesel : type === 'e5' ? $t.map.e5 : $t.map.e10}
							</button>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<div class="header-actions">
			<LanguageSwitcher />
			<button class="theme-toggle" onclick={cycleTheme} aria-label="Toggle theme">
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

	{#if nearbyFetchError}
		<div class="nearby-error-banner">
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
				<line x1="12" y1="9" x2="12" y2="13" />
				<line x1="12" y1="17" x2="12.01" y2="17" />
			</svg>
			{nearbyFetchError}
		</div>
	{/if}

	<div class="station-sidebar" class:open={sidebarOpen}>
		<div class="sidebar-header">
			<h3>{$t.map.nearby} <span class="station-count-badge">{nearbyStations.length}</span></h3>
			<button class="sidebar-close" onclick={() => closeSidebar()} aria-label="Close sidebar">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<line x1="18" y1="6" x2="6" y2="18" />
					<line x1="6" y1="6" x2="18" y2="18" />
				</svg>
			</button>
		</div>
		<div class="sidebar-list">
			{#if isNearbyLoading && nearbyStations.length === 0}
				<div class="sidebar-loading">{$t.map.selectFuel}...</div>
			{:else if nearbyStations.length === 0}
				<div class="sidebar-empty">{$t.map.nearbyFetchFailed}</div>
			{:else}
				{#each sortedNearbyStations as station (station.tankerkoenig_id)}
					{@const address = [station.street, station.house_number, station.post_code, station.place].filter(Boolean).join(', ')}
					{@const price = station[$fuelType] as number | null}
					{@const isCheapest = price !== null && minSelectedFuelPrice !== null && price === minSelectedFuelPrice}
					<button class="station-card" onclick={() => focusStation(station)}>
						<div class="station-card-header">
							<h4>{station.name}</h4>
							<span class="station-card-brand">{station.brand}</span>
						</div>
						{#if address}
							<div class="station-card-address">{address}</div>
						{/if}
						<div class="station-card-meta">
							<span class="open-badge {station.is_open ? 'open' : 'closed'}">
								● {station.is_open ? $t.map.open : $t.map.closed}
							</span>
							{#if userLat !== null && userLng !== null && station.latitude !== null && station.longitude !== null}
								<span class="station-card-distance">
									<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
										<circle cx="12" cy="9" r="2.5" />
									</svg>
									{map ? (map.distance([station.latitude, station.longitude], [userLat, userLng]) / 1000).toFixed(1) : '?'}
									{$t.map.kilometers}
								</span>
							{/if}
						</div>
						<div class="station-card-price" class:cheapest={isCheapest}>
							{#if price !== null}
								{Math.trunc(price)}{$t.map.priceDevider}{price.toFixed(3).split('.')[1]}€
							{:else}
								—
							{/if}
						</div>
					</button>
				{/each}
			{/if}
		</div>
	</div>

	<div class="map-container" bind:this={mapContainer}></div>

	<div class="map-controls glass">
		<div class="station-count">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M3 22V8l9-6 9 6v14H3z" />
				<path d="M9 22V12h6v10" />
			</svg>
			<span>{stations.length} {$t.map.myStations}</span>
			{#if nearbyStations.length > 0}
				<span class="separator">·</span>
				<span>
					{nearbyStations.length}
					{$t.map.nearby}
					{#if isNearbyLoading}
						<span class="loading-spinner"></span>
					{/if}
				</span>
			{/if}
		</div>
		<a href={resolve('/')} class="btn btn-secondary btn-sm">
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M19 12H5M12 19l-7-7 7-7" />
			</svg>
			{$t.map.back}
		</a>
	</div>

	{#if userLat !== null && userLng !== null}
		<div class="zoom-controls">
			<button class="zoom-btn glass" onclick={zoomIn} aria-label="Zoom in">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M12 5v14M5 12h14" />
				</svg>
			</button>
			<button class="zoom-btn glass" onclick={zoomOut} aria-label="Zoom out">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M5 12h14" />
				</svg>
			</button>
		</div>
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
		if (!target.closest('.fuel-selector-wrapper')) {
			showFuelDropdown = false;
		}
	}}
/>
