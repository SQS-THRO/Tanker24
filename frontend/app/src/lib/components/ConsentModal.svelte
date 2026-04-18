<script lang="ts">
	import { privacyStore } from '$lib/stores/privacy';
	import { t } from '$lib/stores/locale';

	function accept() {
		privacyStore.acceptAnalytics();
	}

	function decline() {
		privacyStore.declineAnalytics();
	}
</script>

<div class="modal-overlay" role="dialog" aria-modal="true">
	<div class="modal-content">
		<h2 class="modal-title" id="modal-title">{$t.consent.title}</h2>
		<p class="modal-description">{$t.consent.description}</p>
		<div class="modal-actions">
			<button class="btn btn-secondary" onclick={decline}>
				{$t.consent.decline}
			</button>
			<button class="btn btn-primary" onclick={accept}>
				{$t.consent.accept}
			</button>
		</div>
	</div>
</div>
