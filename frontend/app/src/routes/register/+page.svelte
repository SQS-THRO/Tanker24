<script lang="ts">
	import { resolve } from '$app/paths';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { t } from '$lib/stores/locale';
	import { onMount } from 'svelte';

	onMount(() => {
		if (localStorage.getItem('token')) {
			goto(resolve('/account'));
		}
	});

	let last_name = $state('');
	let first_name = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let invitationKey = $state('');
	let error = $state('');
	let loading = $state(false);
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);

	const emailValid = $derived(() => {
		if (!email) return null;
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return emailRegex.test(email);
	});

	const passwordChecks = $derived({
		minLength: password.length >= 8,
		uppercase: /[A-Z]/.test(password),
		lowercase: /[a-z]/.test(password),
		number: /[0-9]/.test(password),
		special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
	});

	const passwordValid = $derived(passwordChecks.minLength && passwordChecks.uppercase && passwordChecks.lowercase && passwordChecks.number && passwordChecks.special);

	const confirmPasswordValid = $derived(confirmPassword && password === confirmPassword);

	function handleEmailInput() {
		if (email && !emailValid()) {
			error = '';
		}
	}

	async function handleRegister() {
		error = '';
		if (!first_name || !last_name || !email || !password || !confirmPassword || !invitationKey) {
			error = $t.register.fillAllFields;
			return;
		}
		if (password !== confirmPassword) {
			error = $t.register.passwordsNotMatch;
			return;
		}
		if (password.length < 8) {
			error = $t.register.passwordTooShort;
			return;
		}

		loading = true;
		try {
			await authService.register({
				email,
				forename: first_name,
				surname: last_name,
				password,
				invitation_key: invitationKey
			});
			const response = await authService.login({ email, password });
			localStorage.setItem('token', response.access_token);
			await goto(resolve('/account'));
		} catch {
			error = $t.register.registerFailed;
		} finally {
			loading = false;
		}
	}
</script>

<main class="content-centered">
	<div class="background">
		<div class="gradient-orb orb-1"></div>
		<div class="gradient-orb orb-2"></div>
		<div class="grid-pattern"></div>
	</div>

	<Navbar showMapLink={false} showAuthButtons={false} />

	<div class="container">
		<div class="auth-card">
			<div class="card-header">
				<h1>{$t.register.title}</h1>
				<p>{$t.register.subtitle}</p>
			</div>

			<form
				onsubmit={(e) => {
					e.preventDefault();
					handleRegister();
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

				<div class="form-row">
					<div class="form-group">
						<label for="first_name">{$t.register.firstName}</label>
						<input type="text" id="first_name" bind:value={first_name} placeholder={$t.register.firstNamePlaceholder} class="input" disabled={loading} />
					</div>
					<div class="form-group">
						<label for="last_name">{$t.register.lastName}</label>
						<input type="text" id="last_name" bind:value={last_name} placeholder={$t.register.lastNamePlaceholder} class="input" disabled={loading} />
					</div>
				</div>

				<div class="form-group">
					<label for="email">{$t.register.email}</label>
					<div class="input-wrapper">
						<svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
							<polyline points="22,6 12,13 2,6" />
						</svg>
						<input
							type="email"
							id="email"
							bind:value={email}
							oninput={handleEmailInput}
							placeholder={$t.register.emailPlaceholder}
							class="input with-icon"
							class:input-error={email && !emailValid()}
							class:input-success={emailValid()}
							disabled={loading}
						/>
						{#if emailValid()}
							<svg class="validation-icon valid" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<polyline points="20 6 9 17 4 12" />
							</svg>
						{:else if email && !emailValid()}
							<svg class="validation-icon invalid" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<line x1="18" y1="6" x2="6" y2="18" />
								<line x1="6" y1="6" x2="18" y2="18" />
							</svg>
						{/if}
					</div>
					{#if email && !emailValid()}
						<p class="validation-text error">{$t.register.emailInvalid}</p>
					{/if}
				</div>

				<div class="form-group">
					<label for="invitationKey">{$t.register.invitationKey}</label>
					<div class="input-wrapper">
						<svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
						</svg>
						<input type="text" id="invitationKey" bind:value={invitationKey} placeholder={$t.register.invitationKeyPlaceholder} class="input with-icon" disabled={loading} />
					</div>
				</div>

				<div class="form-group">
					<label for="password">{$t.register.password}</label>
					<div class="input-wrapper">
						<svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
							<path d="M7 11V7a5 5 0 0 1 10 0v4" />
						</svg>
						<input
							type={showPassword ? 'text' : 'password'}
							id="password"
							bind:value={password}
							placeholder={$t.register.passwordPlaceholder}
							class="input with-icon toggle-btn"
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
					{#if password}
						<div class="password-checklist">
							<div class="checklist-item" class:valid={passwordChecks.minLength}>
								{#if passwordChecks.minLength}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<polyline points="20 6 9 17 4 12" />
									</svg>
								{:else}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
								{/if}
								<span>{$t.register.passwordMinLength}</span>
							</div>
							<div class="checklist-item" class:valid={passwordChecks.uppercase}>
								{#if passwordChecks.uppercase}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<polyline points="20 6 9 17 4 12" />
									</svg>
								{:else}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
								{/if}
								<span>{$t.register.passwordUppercase}</span>
							</div>
							<div class="checklist-item" class:valid={passwordChecks.lowercase}>
								{#if passwordChecks.lowercase}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<polyline points="20 6 9 17 4 12" />
									</svg>
								{:else}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
								{/if}
								<span>{$t.register.passwordLowercase}</span>
							</div>
							<div class="checklist-item" class:valid={passwordChecks.number}>
								{#if passwordChecks.number}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<polyline points="20 6 9 17 4 12" />
									</svg>
								{:else}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
								{/if}
								<span>{$t.register.passwordNumber}</span>
							</div>
							<div class="checklist-item" class:valid={passwordChecks.special}>
								{#if passwordChecks.special}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<polyline points="20 6 9 17 4 12" />
									</svg>
								{:else}
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<line x1="18" y1="6" x2="6" y2="18" />
										<line x1="6" y1="6" x2="18" y2="18" />
									</svg>
								{/if}
								<span>{$t.register.passwordSpecial}</span>
							</div>
						</div>
					{/if}
				</div>

				<div class="form-group">
					<label for="confirmPassword">{$t.register.confirmPassword}</label>
					<div class="input-wrapper">
						<svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
							<path d="M7 11V7a5 5 0 0 1 10 0v4" />
						</svg>
						<input
							type={showConfirmPassword ? 'text' : 'password'}
							id="confirmPassword"
							bind:value={confirmPassword}
							placeholder={$t.register.confirmPasswordPlaceholder}
							class="input with-icon toggle-btn"
							class:input-error={confirmPassword && !confirmPasswordValid}
							class:input-success={confirmPasswordValid}
							disabled={loading}
						/>
						<button type="button" class="toggle-password" onclick={() => (showConfirmPassword = !showConfirmPassword)}>
							{#if showConfirmPassword}
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
					{#if confirmPassword && !confirmPasswordValid}
						<p class="validation-text error">{$t.register.passwordsNotMatch}</p>
					{/if}
				</div>

				<button type="submit" class="btn btn-primary submit-btn" disabled={loading || !passwordValid || !confirmPasswordValid}>
					{#if loading}
						<span class="spinner"></span>
						{$t.register.creatingAccount}
					{:else}
						{$t.register.createAccount}
					{/if}
				</button>
			</form>

			<div class="divider">
				<span>{$t.register.or}</span>
			</div>

			<p class="footer-text">
				{$t.register.hasAccount} <a href={resolve('/login')}>{$t.register.signIn}</a>
			</p>
		</div>
	</div>
</main>
<Footer />
