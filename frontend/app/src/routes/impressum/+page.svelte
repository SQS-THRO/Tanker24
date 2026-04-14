<script lang="ts">
	import { resolve } from '$app/paths';
	import Navbar from '$lib/components/Navbar.svelte';
	import { t } from '$lib/stores/locale';
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
			<br />
			<p>{$t.impressum.reasoningText}</p>
			<br />
			<p>{$t.impressum.contactAdress}</p>
			<br />
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
			<p>
				{$t.impressum.dataPrivacy}
				<a class="impressum-text" href={resolve('/privacy')}>{$t.impressum.dataPrivacyHeading}</a>
			</p>
		</div>
	</div>
</main>
