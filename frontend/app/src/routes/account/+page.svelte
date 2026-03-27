<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import { t } from '$lib/stores/locale';
	import { themeStore, GLOBAL_THEMES, COLOR_BLIND_OPTIONS, CVD_PALETTES, type ThemePalette } from '$lib/stores/theme';

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

	<nav class="navbar">
		<a href={resolve('/')} class="logo">
			<Logo size={32} />
			<span>Tanker24</span>
		</a>
		<div class="nav-right">
			<LanguageSwitcher />
			<a href={resolve('/map')} class="btn btn-secondary nav-btn">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
					<line x1="9" y1="3" x2="9" y2="18" />
					<line x1="15" y1="6" x2="15" y2="21" />
				</svg>
				{$t.account.viewMap}
			</a>
		</div>
	</nav>

	<div class="container">
		{#if loading}
			<div class="loading">
				<div class="spinner-large"></div>
				<p>{$t.account.loading}</p>
			</div>
		{:else if error}
			<div class="card error-card">
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

			<div class="theme-settings">
				<h2>{$t.account.themeSettings}</h2>

				<div class="setting-group">
					<label class="setting-label">{$t.account.globalTheme}</label>
					<select class="input theme-select">
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
				<div class="card">
					<div class="card-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
							<polyline points="22,6 12,13 2,6" />
						</svg>
					</div>
					<div class="card-content">
						<span class="card-label">{$t.account.emailLabel}</span>
						<span class="card-value">{user.email}</span>
					</div>
				</div>

				<div class="card">
					<div class="card-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
							<circle cx="12" cy="7" r="4" />
						</svg>
					</div>
					<div class="card-content">
						<span class="card-label">{$t.account.nameLabel}</span>
						<span class="card-value">{user.forename} {user.surname || ''}</span>
					</div>
				</div>

				<div class="card stats-card">
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

<style>
	main {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		position: relative;
	}

	.background {
		position: fixed;
		inset: 0;
		pointer-events: none;
		z-index: 0;
	}

	.gradient-orb {
		position: absolute;
		border-radius: 50%;
		filter: blur(100px);
	}

	.orb-1 {
		width: 500px;
		height: 500px;
		background: var(--accent-primary);
		top: -150px;
		right: -100px;
		opacity: 0.12;
	}

	.orb-2 {
		width: 400px;
		height: 400px;
		background: #8b5cf6;
		bottom: -100px;
		left: -100px;
		opacity: 0.08;
	}

	.grid-pattern {
		position: absolute;
		inset: 0;
		background-image: linear-gradient(var(--border-subtle) 1px, transparent 1px), linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
		background-size: 60px 60px;
		mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
		-webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
	}

	.navbar {
		position: relative;
		z-index: 100;
		padding: 1.5rem 2rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
		box-sizing: border-box;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		text-decoration: none;
		color: var(--text-primary);
		font-weight: 700;
		font-size: 1.25rem;
	}

	.nav-right {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		position: relative;
		z-index: 100;
	}

	.nav-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.container {
		flex: 1;
		padding: 2rem;
		position: relative;
		z-index: 10;
		max-width: 700px;
		margin: 0 auto;
		width: 100%;
	}

	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 60vh;
		gap: 1.5rem;
	}

	.loading p {
		color: var(--text-secondary);
	}

	.spinner-large {
		width: 40px;
		height: 40px;
		border: 3px solid var(--border-light);
		border-top-color: var(--accent-primary);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.error-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: 4rem 2rem;
		color: var(--text-secondary);
	}

	.error-card h2 {
		margin-top: 1rem;
		color: var(--text-primary);
	}

	.error-card p {
		margin-bottom: 2rem;
	}

	.profile-header {
		text-align: center;
		margin-bottom: 3rem;
		animation: slideUp 0.5s ease forwards;
	}

	.avatar-large {
		width: 100px;
		height: 100px;
		border-radius: 50%;
		background: var(--accent-gradient);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2.5rem;
		font-weight: 700;
		text-transform: uppercase;
		margin: 0 auto 1.5rem;
		box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
	}

	.profile-header h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	.member-since {
		color: var(--text-secondary);
		font-size: 0.9375rem;
	}

	.cards-grid {
		display: grid;
		gap: 1rem;
		margin-bottom: 2rem;
		animation: slideUp 0.5s ease forwards;
		animation-delay: 100ms;
		opacity: 0;
	}

	.card {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: 1.25rem 1.5rem;
		display: flex;
		align-items: center;
		gap: 1rem;
		transition: all var(--transition-base);
	}

	.card:hover {
		border-color: var(--border-light);
	}

	.card-icon {
		width: 48px;
		height: 48px;
		border-radius: var(--radius-md);
		background: rgba(99, 102, 241, 0.1);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--accent-primary);
		flex-shrink: 0;
	}

	.card-content {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.card-label {
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.card-value {
		font-size: 1rem;
		font-weight: 500;
		color: var(--text-primary);
	}

	.stats-card {
		display: flex;
		justify-content: space-around;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
	}

	.stat-value {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.stat-label {
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.actions-section {
		margin-bottom: 2rem;
		animation: slideUp 0.5s ease forwards;
		animation-delay: 200ms;
		opacity: 0;
	}

	.actions-section h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 1rem;
	}

	.actions-grid {
		display: grid;
		gap: 0.75rem;
	}

	.action-card {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem 1.25rem;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		text-decoration: none;
		color: var(--text-primary);
		transition: all var(--transition-base);
	}

	.action-card:hover {
		border-color: var(--accent-primary);
		background: var(--bg-card-hover);
	}

	.action-card:hover .action-arrow {
		transform: translateX(4px);
	}

	.action-icon {
		width: 40px;
		height: 40px;
		border-radius: var(--radius-sm);
		background: rgba(99, 102, 241, 0.1);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--accent-primary);
	}

	.action-card span {
		flex: 1;
		font-weight: 500;
	}

	.action-arrow {
		color: var(--text-muted);
		transition: transform var(--transition-base);
	}

	.danger-zone {
		border-top: 1px solid var(--border-subtle);
		padding-top: 2rem;
		animation: slideUp 0.5s ease forwards;
		animation-delay: 300ms;
		opacity: 0;
	}

	.danger-zone h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 1rem;
	}

	.btn-danger {
		background: rgba(239, 68, 68, 0.1);
		color: #fca5a5;
		border: 1px solid rgba(239, 68, 68, 0.2);
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.btn-danger:hover {
		background: rgba(239, 68, 68, 0.2);
		border-color: rgba(239, 68, 68, 0.4);
	}

	.theme-settings {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: 1.5rem;
		margin-bottom: 2rem;
	}

	.theme-settings h2 {
		font-size: 1.125rem;
		font-weight: 600;
		margin-bottom: 1.5rem;
		color: var(--text-primary);
	}

	.setting-group {
		margin-bottom: 1.5rem;
	}

	.setting-group:last-child {
		margin-bottom: 0;
	}

	.setting-label {
		display: block;
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.5rem;
	}

	.setting-description {
		font-size: 0.8125rem;
		color: var(--text-muted);
		margin-bottom: 0.75rem;
	}

	.theme-select {
		width: 100%;
		max-width: 300px;
		padding: 0.75rem 1rem;
		font-size: 0.9375rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		color: var(--text-primary);
		cursor: pointer;
	}

	.theme-select:focus {
		outline: none;
		border-color: var(--accent-primary);
	}

	.color-blind-options {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 0.75rem;
	}

	.radio-option {
		display: flex;
		flex-direction: column;
		padding: 0.875rem 1rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.radio-option:hover {
		border-color: var(--accent-primary);
	}

	.radio-option:has(input:checked) {
		border-color: var(--accent-primary);
		background: rgba(99, 102, 241, 0.1);
	}

	.radio-option input {
		appearance: none;
		width: 0;
		height: 0;
		opacity: 0;
		position: absolute;
	}

	.radio-label {
		font-size: 0.9375rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.25rem;
	}

	.radio-description {
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.color-preview {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 1rem;
	}

	.preview-row {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.preview-label {
		font-size: 0.75rem;
		font-weight: 500;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.preview-swatch {
		height: 32px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-light);
	}
</style>
