<script lang="ts">
	import { resolve } from '$app/paths';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import { t } from '$lib/stores/locale';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);
	let showPassword = $state(false);

	async function handleLogin() {
		error = '';
		if (!email || !password) {
			error = $t.login.fillAllFields;
			return;
		}

		loading = true;
		try {
			const response = await authService.login({ email, password });
			localStorage.setItem('token', response.access_token);
			await goto(resolve('/account'));
		} catch {
			error = $t.login.loginFailed;
		} finally {
			loading = false;
		}
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
		<LanguageSwitcher />
	</nav>

	<div class="container">
		<div class="card">
			<div class="card-header">
				<h1>{$t.login.title}</h1>
				<p>{$t.login.subtitle}</p>
			</div>

			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleLogin();
				}}
			>
				{#if error}
					<div class="error-alert">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="12" cy="12" r="10" />
							<line x1="12" y1="8" x2="12" y2="12" />
							<line x1="12" y1="16" x2="12.01" y2="16" />
						</svg>
						{error}
					</div>
				{/if}

				<div class="form-group">
					<label for="email">{$t.login.email}</label>
					<div class="input-wrapper">
						<svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
							<polyline points="22,6 12,13 2,6" />
						</svg>
						<input type="email" id="email" bind:value={email} placeholder={$t.login.emailPlaceholder} class="input with-icon" disabled={loading} />
					</div>
				</div>

				<div class="form-group">
					<label for="password">{$t.login.password}</label>
					<div class="input-wrapper">
						<svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
							<path d="M7 11V7a5 5 0 0 1 10 0v4" />
						</svg>
						<input
							type={showPassword ? 'text' : 'password'}
							id="password"
							bind:value={password}
							placeholder={$t.login.passwordPlaceholder}
							class="input with-icon"
							disabled={loading}
						/>
						<button type="button" class="toggle-password" onclick={() => (showPassword = !showPassword)}>
							{#if showPassword}
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path
										d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
									/>
									<line x1="1" y1="1" x2="23" y2="23" />
								</svg>
							{:else}
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
									<circle cx="12" cy="12" r="3" />
								</svg>
							{/if}
						</button>
					</div>
				</div>

				<button type="submit" class="btn btn-primary submit-btn" disabled={loading}>
					{#if loading}
						<span class="spinner"></span>
						{$t.login.signingIn}
					{:else}
						{$t.login.signIn}
					{/if}
				</button>
			</form>

			<div class="divider">
				<span>{$t.login.or}</span>
			</div>

			<p class="footer-text">
				{$t.login.noAccount} <a href={resolve('/register')}>{$t.login.createOne}</a>
			</p>
		</div>
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
		z-index: 10;
		padding: 1.5rem 2rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
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

	.container {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		position: relative;
		z-index: 10;
	}

	.card {
		width: 100%;
		max-width: 420px;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-xl);
		padding: 2.5rem;
		animation: slideUp 0.5s ease forwards;
	}

	.card-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.card-header h1 {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	.card-header p {
		color: var(--text-secondary);
	}

	.error-alert {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.875rem 1rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: var(--radius-md);
		color: #fca5a5;
		font-size: 0.875rem;
		margin-bottom: 1.5rem;
	}

	.form-group {
		margin-bottom: 1.25rem;
	}

	.form-group label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}

	.input-wrapper {
		position: relative;
	}

	.input-icon {
		position: absolute;
		left: 1rem;
		top: 50%;
		transform: translateY(-50%);
		color: var(--text-muted);
		pointer-events: none;
	}

	.input.with-icon {
		padding-left: 2.75rem;
	}

	.toggle-password {
		position: absolute;
		right: 0.75rem;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color var(--transition-fast);
	}

	.toggle-password:hover {
		color: var(--text-primary);
	}

	.submit-btn {
		width: 100%;
		padding: 0.875rem;
		font-size: 1rem;
		margin-top: 0.5rem;
	}

	.submit-btn:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.spinner {
		width: 18px;
		height: 18px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.divider {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 1.5rem 0;
		color: var(--text-muted);
		font-size: 0.875rem;
	}

	.divider::before,
	.divider::after {
		content: '';
		flex: 1;
		height: 1px;
		background: var(--border-light);
	}

	.footer-text {
		text-align: center;
		color: var(--text-secondary);
		font-size: 0.9375rem;
	}

	.footer-text a {
		color: var(--accent-secondary);
		font-weight: 500;
		text-decoration: none;
		transition: color var(--transition-fast);
	}

	.footer-text a:hover {
		color: var(--accent-primary);
	}
</style>
