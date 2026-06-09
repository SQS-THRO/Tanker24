<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth';
	import { authService } from '$lib/services/auth_api';
	import { exportAsJson, exportAsCsv, downloadBlob } from '$lib/services/export_api';
	import { fillings } from '$lib/stores/fillings';
	import { goto } from '$app/navigation';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import ConfirmModal from '$lib/components/ConfirmModal.svelte';
	import { t } from '$lib/stores/locale';
	import { themeStore, GLOBAL_THEMES, COLOR_BLIND_OPTIONS, CVD_PALETTES, type ThemePalette, type GlobalTheme } from '$lib/stores/theme';

	let user = $state<{
		forename: string;
		surname?: string;
		email: string;
	} | null>(null);
	let loading = $state(true);
	let error = $state('');
	let exporting = $state<'json' | 'csv' | null>(null);
	let showDeleteModal = $state(false);
	let pendingDeleteId = $state<number | null>(null);

	function getPreviewColors(): ThemePalette {
		const override = $themeStore.colorBlindOverride;
		const palette = CVD_PALETTES[override];
		if (palette) return palette;
		return {
			bgPrimary: '#0a0a0b',
			bgSecondary: '#141416',
			bgCard: '#1a1a1d',
			bgCardHover: '#222225',
			bgElevated: '#2a2a2e',
			textPrimary: '#ffffff',
			textSecondary: '#a1a1aa',
			textMuted: '#71717a',
			accentPrimary: '#6366f1',
			accentSecondary: '#818cf8',
			accentGradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%)',
			success: '#22c55e',
			error: '#ef4444',
			warning: '#f59e0b'
		};
	}

	let fillingsToken: string | null = null;

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token) {
			await goto(resolve('/login'));
			return;
		}

		fillingsToken = token;

		try {
			user = await authService.getCurrentUser(token);
			fillings.fetchFillings(token);
		} catch {
			error = $t.account.loadUserFailed;
			localStorage.removeItem('token');
			await goto(resolve('/login'));
		} finally {
			loading = false;
		}
	});

	function handleDelete(fillingId: number) {
		pendingDeleteId = fillingId;
		showDeleteModal = true;
	}

	async function handleConfirmDelete() {
		if (pendingDeleteId === null || !fillingsToken) return;
		const id = pendingDeleteId;
		pendingDeleteId = null;
		showDeleteModal = false;
		try {
			await fillings.removeFilling(fillingsToken, id);
		} catch {
			alert($t.account.deleteFailed);
		}
	}

	function handleCancelDelete() {
		pendingDeleteId = null;
		showDeleteModal = false;
	}

	async function handleLogout() {
		await auth.logout();
		await goto(resolve('/'));
	}

	async function handleExport(format: 'json' | 'csv') {
		const token = localStorage.getItem('token');
		if (!token) return;

		exporting = format;
		try {
			const blob = format === 'json' ? await exportAsJson(token) : await exportAsCsv(token);

			const filename = format === 'json' ? 'user_data.json' : 'car_history_data.csv';

			downloadBlob(blob, filename);
		} catch {
			error = $t.account.exportFailed;
		} finally {
			exporting = null;
		}
	}
</script>

<main>
	<div class="background">
		<div class="gradient-orb orb-1"></div>
		<div class="gradient-orb orb-2"></div>
		<div class="grid-pattern"></div>
	</div>

	<Navbar showAuthButtons={false} />

	<div class="container mt-17" style="flex-direction:column">
		{#if loading}
			<div class="loading">
				<div class="spinner-large"></div>
				<p>{$t.account.loading}</p>
			</div>
		{:else if error}
			<div class="auth-card error-card">
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
					<circle cx="12" cy="12" r="10" />
					<line x1="12" y1="8" x2="12" y2="12" />
					<line x1="12" y1="16" x2="12.01" y2="16" />
				</svg>
				<h2>{$t.account.somethingWrong}</h2>
				<p>{error}</p>
				<a href={resolve('/')} class="btn btn-primary">{$t.account.goHome}</a>
			</div>
		{:else if user}
			<div class="profile-header">
				<div class="avatar-large">
					{user.forename[0]}{user.surname?.[0] || ''}
				</div>
				<h1>{user.forename} {user.surname || ''}</h1>
				<p class="member-since">{$t.account.member}</p>
			</div>

			<div class="theme-settings page-card">
				<h2>{$t.account.themeSettings}</h2>

				<div class="setting-group">
					<label class="setting-label" for="global-theme-select">{$t.account.globalTheme}</label>
					<select
						id="global-theme-select"
						class="input theme-select"
						value={$themeStore.globalTheme}
						onchange={(e) => themeStore.setGlobalTheme(e.currentTarget.value as GlobalTheme)}
					>
						{#each GLOBAL_THEMES as theme (theme.id)}
							<option value={theme.id}>{theme.name}</option>
						{/each}
					</select>
				</div>

				<div class="setting-group">
					<p class="setting-label">{$t.account.colorBlindOverride}</p>
					<p class="setting-description">{$t.account.colorBlindDescription}</p>
					<div class="color-blind-options">
						{#each COLOR_BLIND_OPTIONS as option (option.id)}
							<label class="radio-option">
								<input
									type="radio"
									name="colorBlind"
									value={option.id}
									checked={$themeStore.colorBlindOverride === option.id}
									onchange={() => themeStore.setColorBlindOverride(option.id)}
								/>
								<span class="radio-label">{option.name}</span>
								<span class="radio-description">{option.description}</span>
							</label>
						{/each}
					</div>
				</div>

				<div class="setting-group">
					<p class="setting-label">{$t.account.preview}</p>
					<div class="color-preview">
						<div class="preview-row">
							<span class="preview-label">{$t.account.previewBackground}</span>
							<div class="preview-swatch" style="background-color: {getPreviewColors().bgPrimary}"></div>
							<div class="preview-swatch" style="background-color: {getPreviewColors().bgCard}"></div>
						</div>
						<div class="preview-row">
							<span class="preview-label">{$t.account.previewText}</span>
							<div class="preview-swatch" style="background-color: {getPreviewColors().textPrimary}"></div>
							<div class="preview-swatch" style="background-color: {getPreviewColors().textSecondary}"></div>
						</div>
						<div class="preview-row">
							<span class="preview-label">{$t.account.previewAccent}</span>
							<div class="preview-swatch" style="background-color: {getPreviewColors().accentPrimary}"></div>
							<div class="preview-swatch" style="background-color: {getPreviewColors().accentSecondary}"></div>
						</div>
						<div class="preview-row">
							<span class="preview-label">{$t.account.previewSuccess}</span>
							<div class="preview-swatch" style="background-color: {getPreviewColors().success}"></div>
						</div>
						<div class="preview-row">
							<span class="preview-label">{$t.account.previewError}</span>
							<div class="preview-swatch" style="background-color: {getPreviewColors().error}"></div>
						</div>
						<div class="preview-row">
							<span class="preview-label">{$t.account.previewWarning}</span>
							<div class="preview-swatch" style="background-color: {getPreviewColors().warning}"></div>
						</div>
					</div>
				</div>
			</div>

			<div class="page-card stats-card">
				<div class="stat-item">
					<span class="stat-value">{$t.account.statusActive}</span>
					<span class="stat-label">{$t.account.statusLabel}</span>
				</div>
				<div class="stat-item">
					<span class="stat-value">{$t.account.planFree}</span>
					<span class="stat-label">{$t.account.planLabel}</span>
				</div>
			</div>

			<div class="tanking-section page-card">
				<h2>{$t.account.tankingHistory}</h2>
				{#if $fillings.loading}
					<div class="fillings-loading">
						<div class="spinner"></div>
						<p>{$t.account.loading}</p>
					</div>
				{:else if $fillings.error}
					<div class="fillings-error">
						<p>{$t.account.fillingsLoadFailed}</p>
					</div>
				{:else if $fillings.data.length === 0}
					<p class="fillings-empty">{$t.account.noFillings}</p>
				{:else}
					<div class="fillings-table-wrapper">
						<table class="fillings-table">
							<thead>
								<tr>
									<th>{$t.account.tableLicensePlate}</th>
									<th>{$t.account.tableDate}</th>
									<th>{$t.account.tableMileage}</th>
									<th>{$t.account.tableLiters}</th>
									<th>{$t.account.tablePricePerLiter}</th>
									<th>{$t.account.tableTotal}</th>
									<th>{$t.account.tableFuelType}</th>
									<th>{$t.account.tableDelete}</th>
								</tr>
							</thead>
							<tbody>
								{#each [...$fillings.data].reverse() as filling (filling.id)}
									<tr>
										<td>{filling.license_plate_number}</td>
										<td>{new Date(filling.timestamp).toLocaleDateString()}</td>
										<td>{filling.mileage.toLocaleString()}</td>
										<td>{filling.litres.toFixed(2)}</td>
										<td>{filling.price_per_litre.toFixed(3)} €</td>
										<td>{(filling.price_per_litre * filling.litres).toFixed(2)} €</td>
										<td>{filling.fuel_type.charAt(0).toUpperCase() + filling.fuel_type.slice(1)}</td>
										<td>
											<button class="delete-btn" onclick={() => handleDelete(filling.id!)} aria-label="Delete">
												<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
													<path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
												</svg>
											</button>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</div>

			<div class="export-section page-card">
				<h2>{$t.account.exportSection}</h2>
				<p class="export-description">{$t.account.exportDescription}</p>
				<div class="export-buttons">
					<button class="btn btn-primary" onclick={() => handleExport('json')} disabled={exporting !== null}>
						{#if exporting === 'json'}
							<div class="spinner"></div>
							{$t.account.exporting}
						{:else}
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
								<polyline points="7,10 12,15 17,10" />
								<line x1="12" y1="15" x2="12" y2="3" />
							</svg>
							{$t.account.exportAsJson}
						{/if}
					</button>
					<button class="btn btn-secondary" onclick={() => handleExport('csv')} disabled={exporting !== null}>
						{#if exporting === 'csv'}
							<div class="spinner"></div>
							{$t.account.exporting}
						{:else}
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
								<polyline points="7,10 12,15 17,10" />
								<line x1="12" y1="15" x2="12" y2="3" />
							</svg>
							{$t.account.exportAsCsv}
						{/if}
					</button>
				</div>
			</div>

			<div class="actions-section page-card">
				<h2>{$t.account.quickActions}</h2>
				<div class="actions-grid">
					<a href={resolve('/map')} class="action-card">
						<div class="action-icon">
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
								<line x1="9" y1="3" x2="9" y2="18" />
								<line x1="15" y1="6" x2="15" y2="21" />
							</svg>
						</div>
						<span>{$t.account.viewFuelMap}</span>
						<svg class="action-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M5 12h14M12 5l7 7-7 7" />
						</svg>
					</a>
				</div>
			</div>

			<div class="danger-zone page-card actions-section">
				<h2>{$t.account.accountSection}</h2>
				<button class="btn btn-danger" onclick={handleLogout}>
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
						<polyline points="16,17 21,12 16,7" />
						<line x1="21" y1="12" x2="9" y2="12" />
					</svg>
					{$t.account.signOut}
				</button>
			</div>
		{/if}
	</div>
</main>
<Footer />

<ConfirmModal
	show={showDeleteModal}
	title={$t.account.deleteConfirm}
	message=""
	confirmLabel={$t.account.tableDelete}
	cancelLabel={$t.account.cancel}
	onConfirm={handleConfirmDelete}
	onCancel={handleCancelDelete}
/>

<style>
	.fillings-table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
	}
	.fillings-table th {
		text-align: left;
		padding: 0.5rem 0.4rem;
		border-bottom: 1px solid var(--border-subtle);
		color: var(--text-secondary);
		font-size: 0.8rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		overflow-wrap: break-word;
		white-space: pre-line;
	}
	.fillings-table td {
		padding: 0.5rem 0.4rem;
		border-bottom: 1px solid var(--border-subtle);
		color: var(--text-primary);
		font-size: 0.9rem;
	}
	.delete-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		padding: 0;
		border: none;
		background: none;
		color: var(--text-muted);
		cursor: pointer;
		border-radius: var(--radius-sm);
		transition: all var(--transition-fast);
	}
	.delete-btn:hover {
		background: rgba(239, 68, 68, 0.15);
		color: var(--error);
	}
	.fillings-table tbody tr:hover {
		background: var(--bg-card-hover);
	}
	.fillings-loading,
	.fillings-empty,
	.fillings-error {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 2rem;
		color: var(--text-secondary);
	}
	.fillings-error p {
		color: var(--error);
	}
	.tanking-section h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 1rem;
		text-align: center;
	}
</style>
