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

	// Seed-based pseudo-random for deterministic jitter
	function seededRandom(seed: number): number {
		const x = Math.sin(seed * 9301 + 49297) * 49297;
		return x - Math.floor(x);
	}

	function isInsidePlate(cx: number, cy: number, r: number): boolean {
		const dx = cx - 65;
		const dy = cy - 65;
		return Math.sqrt(dx * dx + dy * dy) + r < 63;
	}

	// Check if a point is part of the digit shape for "1" (left side of plate 1)
	function isDigit1(cx: number, cy: number): boolean {
		// Vertical stroke of "1" - centered around x=48, from y=30 to y=100
		const inVertical = cx >= 44 && cx <= 54 && cy >= 32 && cy <= 98;
		// Top serif/angle
		const inSerif = cx >= 36 && cx <= 48 && cy >= 32 && cy <= 42;
		// Bottom bar
		const inBase = cx >= 36 && cx <= 60 && cy >= 90 && cy <= 98;
		return inVertical || inSerif || inBase;
	}

	// Check if a point is part of the digit shape for "2" (right side of plate 1)
	function isDigit2ForPlate1(cx: number, cy: number): boolean {
		// "2" centered around x=82
		// Top curve - horizontal bar at top
		const topBar = cx >= 68 && cx <= 96 && cy >= 30 && cy <= 40;
		// Right side going down
		const rightSide = cx >= 88 && cx <= 96 && cy >= 36 && cy <= 58;
		// Middle horizontal
		const midBar = cx >= 68 && cx <= 96 && cy >= 56 && cy <= 66;
		// Left side going down
		const leftSide = cx >= 68 && cx <= 76 && cy >= 62 && cy <= 90;
		// Bottom bar
		const bottomBar = cx >= 68 && cx <= 96 && cy >= 88 && cy <= 98;
		return topBar || rightSide || midBar || leftSide || bottomBar;
	}

	// Check if a point is part of the digit "5" for plate 6
	function isDigit5(cx: number, cy: number): boolean {
		// "5" centered in plate
		// Top horizontal bar
		const topBar = cx >= 40 && cx <= 90 && cy >= 28 && cy <= 38;
		// Left vertical from top to middle
		const leftVert = cx >= 40 && cx <= 50 && cy >= 34 && cy <= 62;
		// Middle horizontal bar
		const midBar = cx >= 40 && cx <= 85 && cy >= 56 && cy <= 66;
		// Right vertical from middle to bottom
		const rightVert = cx >= 80 && cx <= 90 && cy >= 62 && cy <= 90;
		// Bottom horizontal bar
		const bottomBar = cx >= 40 && cx <= 90 && cy >= 86 && cy <= 96;
		// Bottom-left corner connector
		const blCorner = cx >= 40 && cx <= 50 && cy >= 82 && cy <= 96;
		return topBar || leftVert || midBar || rightVert || bottomBar || blCorner;
	}

	function generatePlateCircles(digitTest: (cx: number, cy: number) => boolean): Circle[] {
		const circles: Circle[] = [];
		const bgColors = ['#7a8a2e', '#8c9c3d', '#9ab44e', '#a4b84d', '#8fa23d', '#6b7d28', '#b0c858', '#95a83e'];
		const fgColors = ['#cb4a1c', '#d4622a', '#c75820', '#e07040', '#b84418', '#d95a24'];

		let seed = 1;

		// Generate a grid of circles with slight random offsets
		for (let row = 0; row < 18; row++) {
			for (let col = 0; col < 18; col++) {
				const baseX = 8 + col * 7;
				const baseY = 8 + row * 7;
				// Jitter
				const jx = (seededRandom(seed++) - 0.5) * 3;
				const jy = (seededRandom(seed++) - 0.5) * 3;
				const cx = baseX + jx;
				const cy = baseY + jy;
				const r = 2.2 + seededRandom(seed++) * 1.6;

				if (!isInsidePlate(cx, cy, r)) continue;

				const isNumber = digitTest(cx, cy);
				const fill = isNumber ? fgColors[Math.floor(seededRandom(seed++) * fgColors.length)] : bgColors[Math.floor(seededRandom(seed++) * bgColors.length)];

				circles.push({ cx: Math.round(cx * 10) / 10, cy: Math.round(cy * 10) / 10, r: Math.round(r * 10) / 10, fill });
			}
		}

		return circles;
	}

	function digitTestPlate1(cx: number, cy: number): boolean {
		return isDigit1(cx, cy) || isDigit2ForPlate1(cx, cy);
	}

	const plate1Circles = generatePlateCircles(digitTestPlate1);
	const plate6Circles = generatePlateCircles(isDigit5);
</script>

<div class="ishihara-container" class:hidden={!showTest}>
	<h3 class="ishihara-title">{$t.account.ishiharaTest || 'Color Blindness Test'}</h3>
	<p class="ishihara-instructions">
		{$t.account.ishiharaInstructions || 'Look at each plate and identify the number. Compare what you see with and without the color filter to verify it works correctly.'}
	</p>

	<div class="plates-wrapper">
		<div class="plate-item">
			<div class="plate-card">
				<svg viewBox="0 0 130 130" class="ishihara-svg" aria-label="Ishihara Plate 1 - Demonstration plate showing number 12">
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
				<svg viewBox="0 0 130 130" class="ishihara-svg" aria-label="Ishihara Plate 6 - Transformation plate showing number 5">
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
