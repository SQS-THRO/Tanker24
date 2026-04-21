<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { t } from '$lib/stores/locale';
	import { themeStore, GLOBAL_THEMES, COLOR_BLIND_OPTIONS, CVD_PALETTES, type ThemePalette, type GlobalTheme } from '$lib/stores/theme';

	let user = $state<{
		forename: string;
		surname?: string;
		email: string;
	} | null>(null);
	let loading = $state(true);
	let error = $state('');

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

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (!token) {
			await goto(resolve('/login'));
			return;
		}

		try {
			user = await authService.getCurrentUser(token);
		} catch {
			error = $t.account.loadUserFailed;
			localStorage.removeItem('token');
			await goto(resolve('/login'));
		} finally {
			loading = false;
		}
	});

	async function handleLogout() {
		await authService.logout();
		localStorage.removeItem('token');
		await goto(resolve('/'));
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
					<label class="setting-label">{$t.account.globalTheme}</label>
					<select class="input theme-select" value={$themeStore.globalTheme} onchange={(e) => themeStore.setGlobalTheme(e.currentTarget.value as GlobalTheme)}>
						{#each GLOBAL_THEMES as theme (theme.id)}
							<option value={theme.id}>{theme.name}</option>
						{/each}
					</select>
				</div>

				<div class="setting-group">
					<label class="setting-label">{$t.account.colorBlindOverride}</label>
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
					<label class="setting-label">{$t.account.preview}</label>
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

			<div class="cards-grid">
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
			</div>

			<div class="actions-section">
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

			<div class="danger-zone">
				<h3>{$t.account.accountSection}</h3>
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
