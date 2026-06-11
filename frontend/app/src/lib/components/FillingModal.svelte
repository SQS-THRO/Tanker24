<script lang="ts">
	import { t, locale } from '$lib/stores/locale';
	import { fillings, type CreateFillingPayload } from '$lib/stores/fillings';
	import type { TankerkoenigStation } from '$lib/services/stations_api';

	function parseNumber(value: string): number {
		const usesComma = value.includes(',');
		const usesDot = value.includes('.');
		const isGerman = $locale === 'de';

		if (usesComma && usesDot) return NaN;

		if (isGerman) {
			if (usesDot) return NaN;
			return parseFloat(value.replace(',', '.'));
		}

		if (usesComma) return NaN;
		return parseFloat(value);
	}

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

	let touched = $state({
		licensePlate: false,
		carType: false,
		mileage: false,
		litres: false
	});

	const PLATE_REGEX = /^[A-ZÄÖÜ]{1,3}-[A-ZÄÖÜ]{1,2}-\d{1,4}[E|H]?$/i;
	const PLATE_CHARS_REGEX = /^[A-ZÄÖÜ0-9-]+$/i;

	const licensePlateValid = $derived(
		licensePlate.trim().length >= 2 && PLATE_REGEX.test(licensePlate.trim())
	);
	const licensePlateChecks = $derived({
		minLength: licensePlate.trim().length >= 2,
		allowedChars: PLATE_CHARS_REGEX.test(licensePlate.trim()),
		format: PLATE_REGEX.test(licensePlate.trim())
	});
	const carTypeValid = $derived(carType.trim().length >= 1);
	const mileageValid = $derived(mileage !== '' && parseFloat(mileage) > 0);
	const litresValid = $derived(litres !== '' && parseNumber(litres) > 0);
	const litresSeparatorWrong = $derived.by(() => {
		if (litres === '') return false;
		const usesComma = litres.includes(',');
		const usesDot = litres.includes('.');
		const isGerman = $locale === 'de';
		if (usesComma && usesDot) return true;
		if (isGerman) return usesDot;
		return usesComma;
	});

	const fuelTypeLabel = $derived(
		fuelType === 'diesel' ? 'Diesel' : fuelType === 'e5' ? 'E5' : 'E10'
	);

	const stationInfo = $derived.by(() => {
		if (!selectedStationId) return '';
		const station = stations.find((s) => s.tankerkoenig_id === selectedStationId);
		if (!station) return '';
		const addr = [station.street, station.house_number].filter(Boolean).join(' ');
		return `${station.name}${addr ? ` - ${addr}` : ''}`;
	});

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
		touched = {
			licensePlate: false,
			carType: false,
			mileage: false,
			litres: false
		};

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
				litres: parseNumber(litres),
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
					<div class="page-card info-card">
						<div class="info-row">
							<div class="info-item">
								<span class="stat-label">{$t.fillingModal.station}</span>
								<span class="stat-value">{stationInfo}</span>
							</div>
							<div class="info-item">
								<span class="stat-label">{$t.fillingModal.fuelType}</span>
								<span class="stat-value">{fuelTypeLabel}</span>
							</div>
						</div>
						<div class="info-row">
							<div class="info-item">
								<span class="stat-label">{$t.fillingModal.pricePerLitre}</span>
								<span class="stat-value">{pricePerLitre ? `${pricePerLitre} €` : '—'}</span>
							</div>
							<div class="info-item">
								<span class="stat-label">{$t.fillingModal.timestamp}</span>
								<span class="stat-value">{timestamp}</span>
							</div>
						</div>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="plate-input">{$t.fillingModal.licensePlate}</label>
							<input
								id="plate-input"
								type="text"
								class="input"
								class:input-error={touched.licensePlate && !licensePlateValid}
								class:input-success={touched.licensePlate && licensePlateValid}
								placeholder="RO-AB-123"
								bind:value={licensePlate}
								oninput={() => (touched.licensePlate = true)}
							/>
							<div class="password-checklist-wrapper" class:visible={touched.licensePlate}>
								<div class="password-checklist">
									<div class="checklist-item" class:valid={licensePlateChecks.minLength}>
										{#if licensePlateChecks.minLength}
											<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<polyline points="20 6 9 17 4 12" />
											</svg>
										{:else}
											<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<line x1="18" y1="6" x2="6" y2="18" />
												<line x1="6" y1="6" x2="18" y2="18" />
											</svg>
										{/if}
										<span>{$t.fillingModal.licensePlateMinLength}</span>
									</div>
									<div class="checklist-item" class:valid={licensePlateChecks.allowedChars}>
										{#if licensePlateChecks.allowedChars}
											<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<polyline points="20 6 9 17 4 12" />
											</svg>
										{:else}
											<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<line x1="18" y1="6" x2="6" y2="18" />
												<line x1="6" y1="6" x2="18" y2="18" />
											</svg>
										{/if}
										<span>{$t.fillingModal.licensePlateAllowedChars}</span>
									</div>
									<div class="checklist-item" class:valid={licensePlateChecks.format}>
										{#if licensePlateChecks.format}
											<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<polyline points="20 6 9 17 4 12" />
											</svg>
										{:else}
											<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
												<line x1="18" y1="6" x2="6" y2="18" />
												<line x1="6" y1="6" x2="18" y2="18" />
											</svg>
										{/if}
										<span>{$t.fillingModal.licensePlateFormat}</span>
									</div>
								</div>
							</div>
						</div>
						<div class="form-group">
							<label for="car-input">{$t.fillingModal.carType}</label>
							<input
								id="car-input"
								type="text"
								class="input"
								class:input-error={touched.carType && !carTypeValid}
								class:input-success={touched.carType && carTypeValid}
								placeholder="VW Golf"
								bind:value={carType}
								oninput={() => (touched.carType = true)}
							/>
							<div class="field-error-wrapper" class:visible={touched.carType && !carTypeValid}>
								<div class="field-error">
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
									<span>{$t.fillingModal.carTypeRequired}</span>
								</div>
							</div>
						</div>
					</div>

					<div class="form-row">
						<div class="form-group">
							<label for="mileage-input">{$t.fillingModal.mileage}</label>
							<input
								id="mileage-input"
								type="number"
								step="1"
								class="input"
								class:input-error={touched.mileage && !mileageValid}
								class:input-success={touched.mileage && mileageValid}
								placeholder="700"
								bind:value={mileage}
								oninput={() => (touched.mileage = true)}
							/>
							<div class="field-error-wrapper" class:visible={touched.mileage && !mileageValid}>
								<div class="field-error">
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
									<span>{$t.fillingModal.mileageInvalid}</span>
								</div>
							</div>
						</div>
						<div class="form-group">
							<label for="litres-input">{$t.fillingModal.litres}</label>
							<input
								id="litres-input"
								type="text"
								inputmode="decimal"
								class="input"
								class:input-error={touched.litres && !litresValid}
								class:input-success={touched.litres && litresValid}
								placeholder="45.5"
								bind:value={litres}
								oninput={() => (touched.litres = true)}
							/>
							<div class="field-error-wrapper" class:visible={touched.litres && !litresValid}>
								{#if litresSeparatorWrong}
									<div class="field-error">
										<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
											<line x1="18" y1="6" x2="6" y2="18" />
											<line x1="6" y1="6" x2="18" y2="18" />
										</svg>
										<span>{$t.fillingModal.litresWrongSeparator}</span>
									</div>
								{:else}
									<div class="field-error">
										<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
											<line x1="18" y1="6" x2="6" y2="18" />
											<line x1="6" y1="6" x2="18" y2="18" />
										</svg>
										<span>{$t.fillingModal.litresInvalid}</span>
									</div>
								{/if}
							</div>
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

	.info-card {
		margin-bottom: 1.5rem;
		padding: 1rem 1.25rem;
	}

	.info-card .info-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
	}

	.info-card .info-row + .info-row {
		margin-top: 0.75rem;
		padding-top: 0.75rem;
		border-top: 1px solid var(--border-subtle);
	}

	.info-card .info-item {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
	}

	.info-card .stat-label {
		font-size: 0.7rem;
		font-weight: 500;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.info-card .stat-value {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--text-primary);
		word-break: break-word;
	}

	.password-checklist-wrapper.visible .checklist-item:not(.valid) {
		color: var(--error);
	}

	.password-checklist-wrapper.visible .checklist-item:not(.valid) svg {
		color: var(--error);
	}

	.filling-modal-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		margin-top: 0.5rem;
	}
</style>
