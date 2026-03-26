<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/button.svelte';
	import { browser } from '$app/environment';
	import { stationService, type Station } from '$lib/services/stations_api';

	const DEFAULT_LAT = 47.79;
	const DEFAULT_LNG = 12.1;
	const DEFAULT_ZOOM = 11;

	let mapContainer: HTMLDivElement;
	let stations: Station[] = $state([]);
	let error = $state('');
	let userLat = $state<number | null>(null);
	let userLng = $state<number | null>(null);

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

	onMount(async () => {
		if (!browser) return;

		const token = localStorage.getItem('token');
		if (!token) {
			error = 'Please log in to view stations';
			return;
		}

		try {
			stations = await stationService.getStations(token);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load stations';
			return;
		}

		const { lat, lng } = await getUserLocation();
		userLat = lat;
		userLng = lng;

		const L = (await import('leaflet')).default;

		const map = L.map(mapContainer).setView([lat, lng], DEFAULT_ZOOM);

		L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);

		if (userLat !== null && userLng !== null) {
			const userIcon = L.divIcon({
				className: 'user-marker',
				html: '<div style="background-color: #3b82f6; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
				iconSize: [16, 16],
				iconAnchor: [8, 8]
			});
			L.marker([userLat, userLng], { icon: userIcon })
				.addTo(map)
				.bindPopup('Your location')
				.openPopup();
		}

		stations.forEach((station) => {
			if (station.latitude !== null && station.longitude !== null) {
				const marker = L.marker([station.latitude, station.longitude]).addTo(map);
				marker.bindPopup(`<b>${station.name}</b>${station.description ? `<br>${station.description}` : ''}`);
			}
		});
	});
</script>

<main>
	<section class="hero">
		<div class="card">
			<h3>MAP</h3>
			{#if error}
				<p class="error">{error}</p>
			{/if}
			<Button label="Back to Landing Page" href="/" />
		</div>
	</section>
	<div class="map-container" bind:this={mapContainer}></div>
</main>

<style>
	main {
		font-family: system-ui, sans-serif;
		text-align: center;
	}

	section {
		padding: 10px 2rem;
	}

	.hero {
		background: #111;
		color: white;
	}

	.map-container {
		height: 800px;
		width: 100%;
	}

	.error {
		color: #ff6b6b;
		margin: 0.5rem 0;
	}

	:global(.user-marker) {
		background: transparent;
		border: none;
	}
</style>
