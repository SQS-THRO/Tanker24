<script lang="ts">
	import { colorblindMode, type ColorBlindMode } from '$lib/stores/accessibility';
	import { t } from '$lib/stores/locale';
	import IshiharaPlate from './IshiharaPlate.svelte';

	const modes: ColorBlindMode[] = ['none', 'protanopia', 'protanomaly', 'deuteranopia', 'deuteranomaly', 'tritanopia', 'tritanomaly', 'achromatopsia', 'achromatomaly'];

	let showToggles = $state(true);
	let showIshihara = $state(false);

	function selectMode(mode: ColorBlindMode) {
		colorblindMode.set(mode);
	}

	function getModeLabel(mode: ColorBlindMode): string {
		const locale = document.documentElement.lang || 'en';
		const key = `account.colorBlindnessModes.${mode}` as const;
		return ($t as Record<string, Record<string, Record<string, string>>>).account?.colorBlindnessModes?.[mode] || mode;
	}

	function getModeDescription(mode: ColorBlindMode): string {
		const key = `account.colorBlindnessDescriptions.${mode}` as const;
		return ($t as Record<string, Record<string, Record<string, string>>>).account?.colorBlindnessDescriptions?.[mode] || '';
	}
</script>

<section class="accessibility-section" aria-labelledby="accessibility-heading">
	<h2 id="accessibility-heading">{$t.account.accessibility}</h2>

	<div class="setting-header">
		<div class="setting-info">
			<h3 id="colorblindness-label">{$t.account.colorBlindnessMode}</h3>
			<p id="colorblindness-desc">{$t.account.colorBlindnessModeDesc}</p>
		</div>
	</div>

	<div class="segmented-control" role="radiogroup" aria-labelledby="colorblindness-label">
		{#each modes as mode}
			<button
				role="radio"
				aria-checked={$colorblindMode === mode}
				aria-describedby="colorblindness-desc"
				class="segment-option"
				class:active={$colorblindMode === mode}
				onclick={() => selectMode(mode)}
			>
				{getModeLabel(mode)}
			</button>
		{/each}
	</div>

	<div class="toggle-section">
		<button class="toggle-header" onclick={() => (showToggles = !showToggles)} aria-expanded={showToggles}>
			<span>{showToggles ? $t.account.hideToggles : $t.account.showToggles}</span>
			<svg class="toggle-chevron" class:open={showToggles} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M6 9l6 6 6-6" />
			</svg>
		</button>

		{#if showToggles}
			<div class="toggle-grid" role="group" aria-label="Color blindness toggle options">
				{#each modes as mode}
					<label class="toggle-card" class:enabled={$colorblindMode === mode}>
						<input type="radio" name="colorblind-mode" value={mode} checked={$colorblindMode === mode} onchange={() => selectMode(mode)} />
						<div class="toggle-content">
							<span class="toggle-label">{getModeLabel(mode)}</span>
							<span class="toggle-desc">{getModeDescription(mode)}</span>
						</div>
						<div class="toggle-indicator">
							{#if $colorblindMode === mode}
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
									<polyline points="20 6 9 17 4 12" />
								</svg>
							{/if}
						</div>
					</label>
				{/each}
			</div>
		{/if}
	</div>

	<div class="ishihara-toggle">
		<button class="ishihara-toggle-btn" onclick={() => (showIshihara = !showIshihara)} aria-expanded={showIshihara}>
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<circle cx="12" cy="12" r="10" />
				<circle cx="12" cy="12" r="4" />
				<line x1="21.17" y1="8" x2="12" y2="8" />
				<line x1="3.95" y1="6.06" x2="8.54" y2="14" />
				<line x1="10.88" y1="21.94" x2="15.46" y2="14" />
			</svg>
			<span>{showIshihara ? $t.account.ishiharaHide || 'Hide Test Plates' : $t.account.ishiharaShow || 'Show Test Plates'}</span>
			<svg class="toggle-chevron" class:open={showIshihara} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M6 9l6 6 6-6" />
			</svg>
		</button>
	</div>

	{#if showIshihara}
		<IshiharaPlate showTest={true} />
	{/if}
</section>

<style>
	.accessibility-section {
		margin-bottom: 2rem;
		animation: slideUp 0.5s ease forwards;
		animation-delay: 150ms;
		opacity: 0;
	}

	.accessibility-section h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 1rem;
	}

	.setting-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.setting-info h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.25rem;
	}

	.setting-info p {
		font-size: 0.875rem;
		color: var(--text-muted);
	}

	.segmented-control {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		padding: 0.25rem;
		background: var(--bg-secondary);
		border-radius: var(--radius-lg);
		margin-bottom: 1rem;
	}

	.segment-option {
		flex: 1;
		min-width: fit-content;
		padding: 0.625rem 0.75rem;
		font-size: 0.75rem;
		font-weight: 600;
		font-family: inherit;
		background: transparent;
		border: none;
		border-radius: var(--radius-md);
		color: var(--text-muted);
		cursor: pointer;
		transition: all var(--transition-base);
		white-space: nowrap;
	}

	.segment-option:hover {
		color: var(--text-secondary);
		background: var(--bg-card-hover);
	}

	.segment-option.active {
		background: var(--accent-primary);
		color: white;
		box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
	}

	.segment-option:focus-visible {
		outline: 2px solid var(--accent-secondary);
		outline-offset: 2px;
	}

	.toggle-section {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.toggle-header {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.25rem;
		background: none;
		border: none;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		font-family: inherit;
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.toggle-header:hover {
		background: var(--bg-card-hover);
		color: var(--text-primary);
	}

	.toggle-chevron {
		transition: transform var(--transition-base);
	}

	.toggle-chevron.open {
		transform: rotate(180deg);
	}

	.toggle-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 0.5rem;
		padding: 0 0.75rem 0.75rem;
		animation: fadeIn 0.2s ease;
	}

	.toggle-card {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.875rem 1rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.toggle-card:hover {
		border-color: var(--border-light);
		background: var(--bg-card-hover);
	}

	.toggle-card.enabled {
		border-color: var(--accent-primary);
		background: rgba(99, 102, 241, 0.08);
	}

	.toggle-card input[type='radio'] {
		position: absolute;
		opacity: 0;
		pointer-events: none;
	}

	.toggle-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.toggle-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.toggle-desc {
		font-size: 0.75rem;
		color: var(--text-muted);
		line-height: 1.4;
	}

	.toggle-indicator {
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		background: var(--bg-elevated);
		color: var(--accent-primary);
		flex-shrink: 0;
	}

	.toggle-card.enabled .toggle-indicator {
		background: var(--accent-primary);
		color: white;
	}

	.ishihara-toggle {
		margin-top: 1rem;
	}

	.ishihara-toggle-btn {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.875rem 1rem;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		font-family: inherit;
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.ishihara-toggle-btn:hover {
		background: var(--bg-card-hover);
		border-color: var(--border-light);
		color: var(--text-primary);
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 640px) {
		.segmented-control {
			overflow-x: auto;
			flex-wrap: nowrap;
			-webkit-overflow-scrolling: touch;
			scrollbar-width: none;
			padding: 0.375rem;
		}

		.segmented-control::-webkit-scrollbar {
			display: none;
		}

		.segment-option {
			flex: 0 0 auto;
			padding: 0.5rem 0.625rem;
			font-size: 0.6875rem;
		}

		.toggle-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
