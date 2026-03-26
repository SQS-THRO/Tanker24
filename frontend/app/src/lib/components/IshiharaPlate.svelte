<script lang="ts">
	import { t } from '$lib/stores/locale';
	import { colorblindMode } from '$lib/stores/accessibility';

	let { showTest = true } = $props();

	interface Circle {
		cx: number;
		cy: number;
		r: number;
		fill: string;
	}

	const plate1Circles: Circle[] = [
		// Background circles (various greens/yellows)
		{ cx: 50, cy: 50, r: 8, fill: '#8c9c3d' },
		{ cx: 70, cy: 30, r: 10, fill: '#a4b84d' },
		{ cx: 90, cy: 50, r: 9, fill: '#9ab44e' },
		{ cx: 60, cy: 70, r: 11, fill: '#8fa23d' },
		{ cx: 80, cy: 90, r: 8, fill: '#9cb44e' },
		{ cx: 30, cy: 50, r: 10, fill: '#9ab44e' },
		{ cx: 50, cy: 90, r: 9, fill: '#8c9c3d' },
		{ cx: 70, cy: 70, r: 12, fill: '#9cb44e' },
		{ cx: 90, cy: 30, r: 8, fill: '#8fa23d' },
		{ cx: 40, cy: 30, r: 9, fill: '#9ab44e' },
		{ cx: 20, cy: 70, r: 10, fill: '#8c9c3d' },
		{ cx: 100, cy: 70, r: 11, fill: '#9cb44e' },
		{ cx: 30, cy: 90, r: 8, fill: '#8fa23d' },
		{ cx: 110, cy: 50, r: 9, fill: '#9ab44e' },
		{ cx: 60, cy: 110, r: 10, fill: '#8c9c3d' },
		{ cx: 80, cy: 110, r: 8, fill: '#9cb44e' },
		{ cx: 25, cy: 25, r: 7, fill: '#9ab44e' },
		{ cx: 105, cy: 25, r: 9, fill: '#8fa23d' },
		{ cx: 115, cy: 85, r: 8, fill: '#8c9c3d' },
		{ cx: 15, cy: 85, r: 10, fill: '#9cb44e' },
		{ cx: 45, cy: 115, r: 7, fill: '#9ab44e' },
		{ cx: 95, cy: 115, r: 9, fill: '#8fa23d' },
		{ cx: 10, cy: 40, r: 6, fill: '#8c9c3d' },
		{ cx: 120, cy: 40, r: 8, fill: '#9cb44e' },
		{ cx: 10, cy: 100, r: 7, fill: '#9ab44e' },
		{ cx: 120, cy: 100, r: 9, fill: '#8fa23d' },
		{ cx: 35, cy: 10, r: 8, fill: '#8c9c3d' },
		{ cx: 65, cy: 10, r: 6, fill: '#9cb44e' },
		{ cx: 95, cy: 10, r: 7, fill: '#9ab44e' },
		{ cx: 125, cy: 70, r: 5, fill: '#8fa23d' },
		{ cx: 5, cy: 70, r: 6, fill: '#8c9c3d' },
		{ cx: 55, cy: 125, r: 8, fill: '#9cb44e' },
		{ cx: 85, cy: 125, r: 6, fill: '#9ab44e' },
		// Number "12" circles (orange/red - visible to normal, blends for colorblind)
		{ cx: 35, cy: 55, r: 6, fill: '#d4622a' },
		{ cx: 45, cy: 45, r: 5, fill: '#d4622a' },
		{ cx: 40, cy: 65, r: 5, fill: '#c75820' },
		{ cx: 55, cy: 55, r: 6, fill: '#d4622a' },
		{ cx: 50, cy: 45, r: 5, fill: '#c75820' },
		{ cx: 60, cy: 55, r: 5, fill: '#d4622a' },
		{ cx: 55, cy: 70, r: 6, fill: '#c75820' },
		{ cx: 45, cy: 75, r: 5, fill: '#d4622a' },
		{ cx: 65, cy: 45, r: 4, fill: '#d4622a' },
		{ cx: 70, cy: 70, r: 5, fill: '#c75820' },
		{ cx: 75, cy: 55, r: 6, fill: '#d4622a' },
		{ cx: 80, cy: 45, r: 4, fill: '#c75820' },
		{ cx: 85, cy: 65, r: 5, fill: '#d4622a' },
		{ cx: 75, cy: 80, r: 6, fill: '#c75820' },
		{ cx: 65, cy: 85, r: 4, fill: '#d4622a' },
		{ cx: 90, cy: 75, r: 5, fill: '#d4622a' }
	];

	const plate6Circles: Circle[] = [
		// Background circles
		{ cx: 50, cy: 50, r: 9, fill: '#8c9c3d' },
		{ cx: 70, cy: 30, r: 11, fill: '#9ab44e' },
		{ cx: 90, cy: 50, r: 10, fill: '#8fa23d' },
		{ cx: 60, cy: 70, r: 12, fill: '#9cb44e' },
		{ cx: 80, cy: 90, r: 9, fill: '#8c9c3d' },
		{ cx: 30, cy: 50, r: 11, fill: '#9ab44e' },
		{ cx: 50, cy: 90, r: 10, fill: '#8fa23d' },
		{ cx: 70, cy: 70, r: 13, fill: '#9cb44e' },
		{ cx: 90, cy: 30, r: 9, fill: '#8c9c3d' },
		{ cx: 40, cy: 30, r: 10, fill: '#9ab44e' },
		{ cx: 20, cy: 70, r: 11, fill: '#8fa23d' },
		{ cx: 100, cy: 70, r: 12, fill: '#9cb44e' },
		{ cx: 30, cy: 90, r: 9, fill: '#8c9c3d' },
		{ cx: 110, cy: 50, r: 10, fill: '#9ab44e' },
		{ cx: 60, cy: 110, r: 11, fill: '#8fa23d' },
		{ cx: 80, cy: 110, r: 9, fill: '#9cb44e' },
		{ cx: 25, cy: 25, r: 8, fill: '#9ab44e' },
		{ cx: 105, cy: 25, r: 10, fill: '#8fa23d' },
		{ cx: 115, cy: 85, r: 9, fill: '#8c9c3d' },
		{ cx: 15, cy: 85, r: 11, fill: '#9cb44e' },
		{ cx: 45, cy: 115, r: 8, fill: '#9ab44e' },
		{ cx: 95, cy: 115, r: 10, fill: '#8fa23d' },
		{ cx: 10, cy: 40, r: 7, fill: '#8c9c3d' },
		{ cx: 120, cy: 40, r: 9, fill: '#9cb44e' },
		{ cx: 10, cy: 100, r: 8, fill: '#9ab44e' },
		{ cx: 120, cy: 100, r: 10, fill: '#8fa23d' },
		{ cx: 35, cy: 10, r: 9, fill: '#8c9c3d' },
		{ cx: 65, cy: 10, r: 7, fill: '#9cb44e' },
		{ cx: 95, cy: 10, r: 8, fill: '#9ab44e' },
		{ cx: 125, cy: 70, r: 6, fill: '#8fa23d' },
		{ cx: 5, cy: 70, r: 7, fill: '#8c9c3d' },
		{ cx: 55, cy: 125, r: 9, fill: '#9cb44e' },
		{ cx: 85, cy: 125, r: 7, fill: '#9ab44e' },
		// Number "5" / "2" circles (orange - normal sees 5, colorblind sees 2)
		{ cx: 40, cy: 50, r: 5, fill: '#d4622a' },
		{ cx: 50, cy: 40, r: 6, fill: '#c75820' },
		{ cx: 55, cy: 55, r: 5, fill: '#d4622a' },
		{ cx: 45, cy: 65, r: 6, fill: '#c75820' },
		{ cx: 65, cy: 45, r: 5, fill: '#d4622a' },
		{ cx: 70, cy: 60, r: 6, fill: '#c75820' },
		{ cx: 80, cy: 50, r: 5, fill: '#d4622a' },
		{ cx: 75, cy: 70, r: 6, fill: '#c75820' },
		{ cx: 90, cy: 65, r: 5, fill: '#d4622a' },
		{ cx: 60, cy: 75, r: 6, fill: '#c75820' },
		{ cx: 85, cy: 80, r: 5, fill: '#d4622a' },
		{ cx: 50, cy: 85, r: 5, fill: '#d4622a' },
		{ cx: 65, cy: 95, r: 6, fill: '#c75820' },
		{ cx: 80, cy: 95, r: 5, fill: '#d4622a' },
		{ cx: 70, cy: 85, r: 4, fill: '#c75820' },
		{ cx: 35, cy: 70, r: 4, fill: '#d4622a' },
		{ cx: 95, cy: 40, r: 4, fill: '#c75820' },
		{ cx: 30, cy: 55, r: 3, fill: '#d4622a' },
		{ cx: 100, cy: 80, r: 3, fill: '#c75820' }
	];
</script>

<div class="ishihara-container" class:hidden={!showTest}>
	<h3 class="ishihara-title">{$t.account.ishiharaTest || 'Color Blindness Test'}</h3>
	<p class="ishihara-instructions">
		{$t.account.ishiharaInstructions || 'Look at each plate and identify the number. Compare what you see with and without the color filter to verify it works correctly.'}
	</p>

	<div class="plates-wrapper">
		<div class="plate-item">
			<div class="plate-card">
				<svg viewBox="0 0 130 130" class="ishihara-svg" aria-label="Ishihara Plate 1 - Demonstration plate">
					<circle cx="65" cy="65" r="65" fill="#1a1a1d" />
					{#each plate1Circles as circle, i (i)}
						<circle cx={circle.cx} cy={circle.cy} r={circle.r} fill={circle.fill} />
					{/each}
				</svg>
			</div>
			<p class="plate-label">{$t.account.ishiharaPlate1 || 'Plate 1: Demonstration'}</p>
			<p class="plate-answer">{$t.account.ishiharaPlate1Answer || 'You should see: 12'}</p>
		</div>

		<div class="plate-item">
			<div class="plate-card">
				<svg viewBox="0 0 130 130" class="ishihara-svg" aria-label="Ishihara Plate 6 - Transformation plate">
					<circle cx="65" cy="65" r="65" fill="#1a1a1d" />
					{#each plate6Circles as circle, i (i)}
						<circle cx={circle.cx} cy={circle.cy} r={circle.r} fill={circle.fill} />
					{/each}
				</svg>
			</div>
			<p class="plate-label">{$t.account.ishiharaPlate6 || 'Plate 6: Transformation'}</p>
			<p class="plate-answer">{$t.account.ishiharaPlate6Answer || 'Normal: 5 | Red/Green color blind: 2'}</p>
		</div>
	</div>

	<div class="current-mode">
		<span class="mode-label">Current filter:</span>
		<span class="mode-value">{$colorblindMode}</span>
	</div>
</div>

<style>
	.ishihara-container {
		margin-top: 1.5rem;
		padding: 1.25rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		animation: fadeIn 0.3s ease;
	}

	.ishihara-container.hidden {
		display: none;
	}

	.ishihara-title {
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.5rem;
	}

	.ishihara-instructions {
		font-size: 0.875rem;
		color: var(--text-muted);
		margin-bottom: 1.25rem;
		line-height: 1.5;
	}

	.plates-wrapper {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.plate-item {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.plate-card {
		width: 100%;
		max-width: 140px;
		aspect-ratio: 1;
		border-radius: 50%;
		overflow: hidden;
		border: 3px solid var(--border-light);
		background: #1a1a1d;
	}

	.ishihara-svg {
		width: 100%;
		height: 100%;
	}

	.plate-label {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-top: 0.75rem;
		text-align: center;
	}

	.plate-answer {
		font-size: 0.75rem;
		color: var(--text-muted);
		margin-top: 0.25rem;
		text-align: center;
	}

	.current-mode {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		background: rgba(99, 102, 241, 0.1);
		border-radius: var(--radius-md);
		font-size: 0.8125rem;
	}

	.mode-label {
		color: var(--text-muted);
	}

	.mode-value {
		color: var(--accent-primary);
		font-weight: 600;
		text-transform: capitalize;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@media (max-width: 480px) {
		.plates-wrapper {
			grid-template-columns: 1fr;
		}

		.plate-card {
			max-width: 180px;
		}
	}
</style>
