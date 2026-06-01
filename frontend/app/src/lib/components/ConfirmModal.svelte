<script lang="ts">
	const {
		show = false,
		title = '',
		message = '',
		confirmLabel = 'Delete',
		cancelLabel = 'Cancel',
		onConfirm = () => {},
		onCancel = () => {}
	} = $props<{
		show: boolean;
		title: string;
		message: string;
		confirmLabel?: string;
		cancelLabel?: string;
		onConfirm: () => void;
		onCancel: () => void;
	}>();

	function handleOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onCancel();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			onCancel();
		}
	}
</script>

{#if show}
	<div class="modal-overlay" role="dialog" aria-modal="true" tabindex="-1" onclick={handleOverlayClick} onkeydown={handleKeydown}>
		<div class="modal-content" role="document">
			<div class="modal-icon modal-icon-danger">
				<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
				</svg>
			</div>
			<h2 class="modal-title">{title}</h2>
			<p class="modal-description">{message}</p>
			<div class="modal-actions">
				<button class="btn btn-secondary" onclick={onCancel}>
					{cancelLabel}
				</button>
				<button class="btn btn-danger" onclick={onConfirm}>
					{confirmLabel}
				</button>
			</div>
		</div>
	</div>
{/if}
