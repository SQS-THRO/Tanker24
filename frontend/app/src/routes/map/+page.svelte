<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { resolve } from '$app/paths';
	import { stationService, type TankerkoenigStation } from '$lib/services/stations_api';
	import { auth } from '$lib/stores/auth';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import AuthRequiredModal from '$lib/components/AuthRequiredModal.svelte';
	import FillingModal from '$lib/components/FillingModal.svelte';
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
	const fuelTypes: FuelType[] = ['diesel', 'e5', 'e10'];
	const cycleOrder: GlobalTheme[] = ['dark-modern', 'light-modern', 'auto'];

	let L: typeof import('leaflet').default;
	let mapContainer: HTMLDivElement;
	let nearbyStations: TankerkoenigStation[] = $state([]);
	let sortedNearbyStations: TankerkoenigStation[] = $state([]);
	let filteredStations: TankerkoenigStation[] = $derived.by(() => {
		const searched = searchQuery.trim()
			? sortedNearbyStations.filter(
					(s) =>
						s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
						s.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
						(s.street && s.street.toLowerCase().includes(searchQuery.toLowerCase()))
				)
			: sortedNearbyStations;
		if (!map) return searched;
		const bounds = map.getBounds();
		const center = bounds.getCenter();
		const northEast = bounds.getNorthEast();
		const viewRadius = center.distanceTo(northEast);
		return searched.filter((station) => {
			if (station.latitude == null || station.longitude == null) return false;
			const dist = map.distance([station.latitude, station.longitude], [currentCenterLat, currentCenterLng]);
			return dist <= viewRadius;
		});
	});
	let minSelectedFuelPrice: number | null = $state(null);
	let knownStations = new Map<string, TankerkoenigStation>();
	let nearbyFetchError = $state('');
	let searchQuery = $state('');
	let userLat = $state<number | null>(null);
	let userLng = $state<number | null>(null);
	let currentCenterLat = $state(DEFAULT_LAT);
	let currentCenterLng = $state(DEFAULT_LNG);
	let user = $state<{ forename: string; surname?: string } | null>(null);
	let showUserMenu = $state(false);
	let showAuthModal = $state(false);
	let showFillingModal = $state(false);
	let fillingStationId = $state('');
	let map: Map | null = $state(null);
	let tileLayer: ReturnType<L['tileLayer']> | null = null;
	let userLocationMarker: Marker | null = null;
	let nearbyLayerGroup: LayerGroup | null = null;
	let moveDebounceTimer: ReturnType<typeof setTimeout> | null = null;
	let isNearbyLoading = $state(false);
	let showFuelDropdown = $state(false);
	let sidebarOpen = $state(false);
	let apiToken = $state('');
	let manuallyClosed = false;
	let nearbyMarkersMap = new Map<string, Marker>();
	let themeInitialized = false;
	let localeInitialized = false;

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

	function cycleTheme() {
		const current = $themeStore.globalTheme;
		const nextIndex = (cycleOrder.indexOf(current) + 1) % cycleOrder.length;
		themeStore.setGlobalTheme(cycleOrder[nextIndex]);
	}

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
	}

	function refreshPopups() {
		if (!map || !L) return;

		if (userLocationMarker && userLat !== null && userLng !== null) {
			userLocationMarker.setPopupContent(`<div class="popup user-popup"><strong>${$t.map.yourLocation}</strong></div>`);
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
					<button class="popup-record-btn" onclick="window.dispatchEvent(new CustomEvent('open-filling-modal', {detail: {stationId: '${station.tankerkoenig_id}'}}))">
						${$t.fillingModal.record}
					</button>
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

	function handleOpenFillingModal(e: Event) {
		const detail = (e as CustomEvent).detail;
		if (detail?.stationId) {
			fillingStationId = detail.stationId;
			showFillingModal = true;
		}
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
		apiToken = token;

		await loadUser();

		const { lat, lng } = await getUserLocation();
		userLat = lat;
		userLng = lng;

		map = L.map(mapContainer, { zoomControl: false }).setView([lat, lng], DEFAULT_ZOOM);

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

		await fetchNearbyStations(lat, lng);

		map.on('moveend', () => {
			if (!map) return;
			const center = map.getCenter();
			currentCenterLat = center.lat;
			currentCenterLng = center.lng;
			debounce(async () => {
				await fetchNearbyStations(center.lat, center.lng);
			}, NEARBY_DEBOUNCE_MS);
		});
	});

	onMount(() => {
		window.addEventListener('open-filling-modal', handleOpenFillingModal);
		return () => window.removeEventListener('open-filling-modal', handleOpenFillingModal);
	});

	onDestroy(() => {
		if (moveDebounceTimer) clearTimeout(moveDebounceTimer);
		if (map) {
			map.off('moveend');
			map.remove();
		}
	});
</script>

<main>
	<AuthRequiredModal show={showAuthModal} />
	<FillingModal
		show={showFillingModal}
		onClose={() => {
			showFillingModal = false;
			fillingStationId = '';
		}}
		stations={nearbyStations}
		initialFuelType={$fuelType}
		token={apiToken}
		prefillStationId={fillingStationId}
	/>
	<div class="map-header glass">
		<button class="sidebar-toggle glass" onclick={() => openSidebar()} aria-label="Toggle station list">
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<line x1="3" y1="6" x2="21" y2="6" />
				<line x1="3" y1="12" x2="21" y2="12" />
				<line x1="3" y1="18" x2="21" y2="18" />
			</svg>
		</button>
		<a href={resolve('/')} class="navbar-logo header-logo">
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
			{#if user}
				<div class="profile-wrapper header-profile">
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
			<h3>{$t.map.nearby} <span class="station-count-badge">{filteredStations.length}</span></h3>
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
			{:else if filteredStations.length === 0}
				<div class="sidebar-empty">{$t.map.searchNoResults}</div>
			{:else}
				{#each filteredStations as station (station.tankerkoenig_id)}
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
			<svg height="18" width="18" version="1.1" id="_x32_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve">
				<style type="text/css">
					.st0 {
						fill: var(--text-secondary);
					}
				</style>
				<g>
					<path
						class="st0"
						d="M485.395,158.609c-7.296-8.514-12.122-13.426-20.826-22.348c-27.93-28.573-53.191-53.843-53.218-53.869
						l-12.591-12.6l-17.435,17.026l36.061,54.731l0.374,0.765c0.191,0.591,0.374,1.566,0.374,2.826c0.052,2.704-0.974,6.609-2.479,9.313
						l-3.165,5.826c-3.661,6.756-5.713,21.113-5.705,28.574c-0.008,7.182,1.696,14.4,5.114,20.982l6.235,12.026
						c7.295,14.07,21.347,23.148,36.991,24.348l3,0.939c0,39.574,0,88.904,0,126.835c-0.052,11.043-3.296,17.617-6.888,21.635
						c-3.652,3.991-7.965,5.634-11.913,5.644c-3.826-0.07-7.217-1.348-10.417-4.948c-3.13-3.617-6.365-10.295-6.4-22.33
						c0-35.618,0-44.522,0-66.783c-0.009-7.113-1.436-14.156-4.044-20.974c-3.93-10.191-10.601-20-20.348-27.582
						c-9.678-7.583-22.678-12.592-37.226-12.539c-1.704,0-3.425,0.096-5.164,0.226V47.956C355.726,21.469,334.256,0,307.769,0H97.378
						C70.891,0,49.422,21.469,49.422,47.956v406.166H18.256V512h368.634v-57.878h-31.165V282.174c1.843-0.27,3.6-0.452,5.164-0.452
						c4.496,0.017,8.01,0.93,11.096,2.4c4.592,2.192,8.374,5.896,11.026,10.348c2.67,4.382,3.922,9.461,3.879,12.73
						c0,22.261,0,31.165,0,66.783c-0.035,18.556,5.312,34.417,15.13,45.695c9.739,11.305,23.66,17.279,37.304,17.209
						c14.183,0.008,28.174-6.165,38.296-17.339c10.174-11.165,16.174-27.148,16.122-45.565c0-57.878,0-150.261,0-185.878
						C493.743,171.409,492.074,166.4,485.395,158.609z M284.491,227.061H120.656V71.235h163.834V227.061z M458.126,212.009
						c0,2.808-1.609,4.122-3.896,4.078c-4.304-0.07-11.009-1-13.913-5.722c-5.191-8.435-12.183-24.87-4.609-37.756
						c0.808-1.374,2.574-3.583,5.722-1.478l10.13,9.304c4.182,3.826,6.565,9.226,6.565,14.895
						C458.126,195.33,458.126,209.2,458.126,212.009z"
					/>
				</g>
			</svg>
			{#if filteredStations.length > 0}
				<span>
					{filteredStations.length}
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
