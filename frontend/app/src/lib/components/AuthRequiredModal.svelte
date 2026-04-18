<script lang="ts">
	import { resolve } from '$app/paths';
	import { goto } from '$app/navigation';
	import { t } from '$lib/stores/locale';

	const { show = false } = $props<{ show: boolean }>();

	function handleBack() {
		window.history.back();
	}

	function handleLogin() {
		goto(resolve('/login'));
	}

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			handleBack();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			handleBack();
		}
	}
</script>

{#if show}
	<div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1" onclick={handleOverlayClick} onkeydown={handleKeydown}>
		<div class="modal-content" role="document">
			<div class="modal-icon">
				<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
					<path d="M7 11V7a5 5 0 0 1 10 0v4" />
				</svg>
			</div>
			<h2 class="modal-title" id="modal-title">{$t.authRequired.title}</h2>
			<p class="modal-description">{$t.authRequired.description}</p>
			<div class="modal-actions">
				<button class="btn btn-secondary" onclick={handleBack}>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M19 12H5M12 19l-7-7 7-7" />
					</svg>
					{$t.authRequired.back}
				</button>
				<button class="btn btn-primary" onclick={handleLogin}>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
						<polyline points="10,17 15,12 10,7" />
						<line x1="15" y1="12" x2="3" y2="12" />
					</svg>
					{$t.authRequired.login}
				</button>
			</div>
		</div>
	</div>
{/if}
