<script lang="ts">
	import { t } from '$lib/stores/locale';
	import { fillings, type CreateFillingPayload } from '$lib/stores/fillings';
	import type { TankerkoenigStation } from '$lib/services/stations_api';

	const {
		show = false,
		onClose,
		stations = [],
		initialFuelType = 'e5',
		token = '',
		prefillStationId = ''
	} = $props<{
		show: boolean;
		onClose: () => void;
		stations: TankerkoenigStation[];
		initialFuelType: string;
		token: string;
		prefillStationId?: string;
	}>();

	let fuelType = $state('');
	let selectedStationId = $state('');
	let pricePerLitre = $state('');
	let timestamp = $state('');
	let licensePlate = $state('');
	let carType = $state('');
	let mileage = $state('');
	let litres = $state('');
	let submitting = $state(false);
	let error = $state('');
	let success = $state('');

	function resetForm() {
		fuelType = initialFuelType;
		selectedStationId = prefillStationId;
		pricePerLitre = '';
		timestamp = new Date().toISOString().slice(0, 16);
		licensePlate = '';
		carType = '';
		mileage = '';
		litres = '';
		error = '';
		success = '';
		submitting = false;

		if (selectedStationId && fuelType) {
			const station = stations.find((s) => s.tankerkoenig_id === selectedStationId);
			if (station) {
				const price = station[fuelType as 'diesel' | 'e5' | 'e10'];
				if (price !== null && price !== undefined) {
					pricePerLitre = price.toFixed(3);
				}
			}
		}
	}

	$effect(() => {
		if (show) {
			resetForm();
		}
	});

	function handleStationChange(e: Event) {
		const stationId = (e.currentTarget as HTMLSelectElement).value;
		selectedStationId = stationId;
		if (stationId && fuelType) {
			const station = stations.find((s) => s.tankerkoenig_id === stationId);
			if (station) {
				const price = station[fuelType as 'diesel' | 'e5' | 'e10'];
				if (price !== null && price !== undefined) {
					pricePerLitre = price.toFixed(3);
				}
			}
		}
	}

	function handleFuelTypeChange(e: Event) {
		const ft = (e.currentTarget as HTMLSelectElement).value;
		fuelType = ft;
		if (selectedStationId && ft) {
			const station = stations.find((s) => s.tankerkoenig_id === selectedStationId);
			if (station) {
				const price = station[ft as 'diesel' | 'e5' | 'e10'];
				if (price !== null && price !== undefined) {
					pricePerLitre = price.toFixed(3);
				}
			}
		}
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onClose();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			onClose();
		}
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!selectedStationId || !fuelType || !pricePerLitre || !licensePlate || !carType || !mileage || !litres || !timestamp) {
			error = $t.fillingModal.fillRequired;
			return;
		}

		submitting = true;
		error = '';

		try {
			const payload: CreateFillingPayload = {
				license_plate_number: licensePlate.trim().toUpperCase(),
				car_type: carType.trim(),
				mileage: parseFloat(mileage),
				timestamp: new Date(timestamp).toISOString(),
				price_per_litre: parseFloat(pricePerLitre),
				litres: parseFloat(litres),
				tankerkoenig_station_id: selectedStationId,
				fuel_type: fuelType as 'diesel' | 'e5' | 'e10'
			};

			await fillings.createFilling(token, payload);
			success = $t.fillingModal.success;
			setTimeout(() => {
				onClose();
			}, 1500);
		} catch (e) {
			error = e instanceof Error ? e.message : $t.fillingModal.error;
		} finally {
			submitting = false;
		}
	}
</script>

{#if show}
	<div class="modal-overlay" role="dialog" aria-modal="true" tabindex="-1" onclick={handleOverlayClick} onkeydown={handleKeydown}>
		<div class="modal-content filling-modal-content">
			<h2 class="modal-title">{$t.fillingModal.title}</h2>

			{#if success}
				<div class="filling-success">
					<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2">
						<circle cx="12" cy="12" r="10" />
						<path d="M8 12l2 2 4-4" />
					</svg>
					<p>{success}</p>
				</div>
			{:else}
				{#if error}
					<div class="error-alert">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="12" cy="12" r="10" />
							<line x1="12" y1="8" x2="12" y2="12" />
							<line x1="12" y1="16" x2="12.01" y2="16" />
						</svg>
						{error}
					</div>
				{/if}

				<form onsubmit={handleSubmit}>
					<div class="form-row">
						<div class="form-group">
							<label for="ft-select">{$t.fillingModal.fuelType}</label>
							<select id="ft-select" class="input" value={fuelType} onchange={handleFuelTypeChange}>
								<option value="diesel">Diesel</option>
								<option value="e5">E5</option>
								<option value="e10">E10</option>
							</select>
						</div>
						<div class="form-group">
							<label for="station-select">{$t.fillingModal.station}</label>
							<select id="station-select" class="input" value={selectedStationId} onchange={handleStationChange}>
								<option value="">{$t.fillingModal.stationPlaceholder}</option>
								{#each stations as station (station.tankerkoenig_id)}
									{@const addr = [station.street, station.house_number].filter(Boolean).join(' ')}
									<option value={station.tankerkoenig_id}>
										{station.name}{addr ? ` - ${addr}` : ''}
									</option>
								{/each}
							</select>
						</div>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="price-input">{$t.fillingModal.pricePerLitre}</label>
							<input id="price-input" type="number" step="0.001" class="input" placeholder="1.859" bind:value={pricePerLitre} />
						</div>
						<div class="form-group">
							<label for="ts-input">{$t.fillingModal.timestamp}</label>
							<input id="ts-input" type="datetime-local" class="input" bind:value={timestamp} />
						</div>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="plate-input">{$t.fillingModal.licensePlate}</label>
							<input id="plate-input" type="text" class="input" placeholder="RO-AB-123" bind:value={licensePlate} />
						</div>
						<div class="form-group">
							<label for="car-input">{$t.fillingModal.carType}</label>
							<input id="car-input" type="text" class="input" placeholder="VW Golf" bind:value={carType} />
						</div>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="mileage-input">{$t.fillingModal.mileage}</label>
							<input id="mileage-input" type="number" step="1" class="input" placeholder="700" bind:value={mileage} />
						</div>
						<div class="form-group">
							<label for="litres-input">{$t.fillingModal.litres}</label>
							<input id="litres-input" type="number" step="0.01" class="input" placeholder="45.5" bind:value={litres} />
						</div>
					</div>

					<div class="filling-modal-actions">
						<button type="button" class="btn btn-secondary" onclick={onClose} disabled={submitting}>
							{$t.fillingModal.cancel}
						</button>
						<button type="submit" class="btn btn-primary" disabled={submitting}>
							{#if submitting}
								<div class="spinner"></div>
							{/if}
							{submitting ? $t.fillingModal.submitting : $t.fillingModal.submit}
						</button>
					</div>
				</form>
			{/if}
		</div>
	</div>
{/if}

<style>
	.filling-modal-content {
		max-width: 520px;
		text-align: left;
	}

	.filling-modal-content .modal-title {
		font-size: 1.25rem;
		font-weight: 700;
		margin-bottom: 1.5rem;
		color: var(--text-primary);
	}

	.filling-success {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		padding: 2rem 0;
		color: var(--success);
		font-weight: 600;
		font-size: 1rem;
	}

	.filling-modal-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		margin-top: 0.5rem;
	}
</style>
