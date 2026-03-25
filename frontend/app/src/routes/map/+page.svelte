<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/button.svelte';
	import { browser } from '$app/environment';
	import { stationService, type Station } from '$lib/services/stations';

	let mapContainer: HTMLDivElement;
	let stations: Station[] = $state([]);
	let error = $state('');

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

		const L = (await import('leaflet')).default;

		const map = L.map(mapContainer).setView([47.79, 12.1], 11);

		L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
			maxZoom: 19,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);

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
</style>
