<script lang="ts">
	import { resolve } from '$app/paths';
	import { authService } from '$lib/services/auth_api';
	import { goto } from '$app/navigation';
	import Navbar from '$lib/components/Navbar.svelte';
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

	<Navbar showMapLink={false} showAuthButtons={false} />

	<div class="container">
		<div class="content-card">
			<h1>{$t.impressum.pageTitle}</h1>
			<div class="divider-nogap"></div>
			<p>{$t.impressum.contactAdress}</p>
			<p class="bolder">{$t.impressum.contactRepresentativeHeading}</p>
			<p>{$t.impressum.contactRepresentative}</p>

			<div class="divider-nogap"></div>

			<h2>{$t.impressum.contactHeading}</h2>
			<p>{$t.impressum.contactPhone}</p>
			<p>{$t.impressum.contactEmail}</p>

			<div class="divider-nogap"></div>

			<h2>{$t.impressum.copyrightHeading}</h2>
			<p>{$t.impressum.copyright}</p>

			<div class="divider-nogap"></div>

			<h2>{$t.impressum.dataPrivacyHeading}</h2>
			<p>{$t.impressum.dataPrivacy}
				<a class="impressum-text" href={resolve('/privacy')}>{$t.impressum.dataPrivacyHeading}</a>
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
</style>
