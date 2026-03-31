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

<style>
	.modal-overlay {
		position: fixed;
		inset: 0;
		z-index: 9999;
		background: rgba(0, 0, 0, 0.6);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
		animation: fadeIn 0.15s ease;
	}

	.modal-content {
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-lg);
		padding: 2rem;
		max-width: 400px;
		width: 100%;
		text-align: center;
		box-shadow: var(--shadow-xl);
		animation: scaleIn 0.2s ease;
	}

	.modal-icon {
		width: 64px;
		height: 64px;
		margin: 0 auto 1.5rem;
		border-radius: 50%;
		background: rgba(99, 102, 241, 0.15);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--accent-primary);
	}

	.modal-title {
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--text-primary);
		margin: 0 0 0.5rem;
	}

	.modal-description {
		font-size: 0.9375rem;
		color: var(--text-secondary);
		margin: 0 0 1.5rem;
		line-height: 1.5;
	}

	.modal-actions {
		display: flex;
		gap: 0.75rem;
	}

	.modal-actions .btn {
		flex: 1;
		justify-content: center;
	}

	.btn {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		font-size: 0.875rem;
		font-weight: 500;
		border-radius: var(--radius-md);
		text-decoration: none;
		cursor: pointer;
		transition: all var(--transition-base);
		border: none;
		font-family: inherit;
	}

	.btn-primary {
		background: var(--accent-gradient);
		color: white;
	}

	.btn-primary:hover {
		opacity: 0.9;
		transform: translateY(-1px);
	}

	.btn-secondary {
		background: var(--bg-secondary);
		color: var(--text-primary);
		border: 1px solid var(--border-light);
	}

	.btn-secondary:hover {
		background: var(--bg-card-hover);
		border-color: var(--accent-primary);
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes scaleIn {
		from {
			opacity: 0;
			transform: scale(0.95);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}
</style>
