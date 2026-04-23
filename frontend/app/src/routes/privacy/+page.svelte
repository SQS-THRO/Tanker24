<script lang="ts">
	import Navbar from '$lib/components/Navbar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { t } from '$lib/stores/locale';
</script>

<main>
	<div class="background">
		<div class="gradient-orb orb-1"></div>
		<div class="gradient-orb orb-2"></div>
		<div class="grid-pattern"></div>
	</div>

	<Navbar showMapLink={false} showAuthButtons={false} />

	<div class="container mt-17">
		<div class="content-card">
			<h1>{$t.privacy.pageTitle}</h1>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.controllerHeading}</h2>
				<p>{$t.privacy.controller}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.collectionHeading}</h2>
				<p>{$t.privacy.collection}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.purposeHeading}</h2>
				<p>{$t.privacy.purpose}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.legalBasisHeading}</h2>
				<p>{$t.privacy.legalBasis}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.recipientsHeading}</h2>
				<p>{$t.privacy.recipients}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.retentionHeading}</h2>
				<p>{$t.privacy.retention}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.rightsHeading}</h2>
				<p>{$t.privacy.rightsIntro}</p>
				<ul>
					<li>{$t.privacy.rightAccess}</li>
					<li>{$t.privacy.rightRectification}</li>
					<li>{$t.privacy.rightErasure}</li>
					<li>{$t.privacy.rightRestriction}</li>
					<li>{$t.privacy.rightPortability}</li>
					<li>{$t.privacy.rightObject}</li>
				</ul>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.withdrawHeading}</h2>
				<p>{$t.privacy.withdraw}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.complaintHeading}</h2>
				<p>{$t.privacy.complaint}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.externalLinksHeading}</h2>
				<p>{$t.privacy.externalLinks}</p>
			</section>

			<div class="divider-nogap"></div>

			<section>
				<h2>{$t.privacy.amendmentHeading}</h2>
				<p>{$t.privacy.amendment}</p>
			</section>
		</div>
	</div>
</main>
<Footer />
