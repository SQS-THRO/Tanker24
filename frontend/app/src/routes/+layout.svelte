<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { colorblindMode } from '$lib/stores/accessibility';

	let { children } = $props();

	let currentFilter = $state<string | null>(null);

	$effect(() => {
		const unsub = colorblindMode.subscribe((mode) => {
			currentFilter = mode === 'none' ? null : mode;
		});
		return unsub;
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
	<title>Tanker24</title>
</svelte:head>

<!-- SVG filters for color blindness simulation -->
<svg xmlns="http://www.w3.org/2000/svg" class="svg-filters" aria-hidden="true">
	<defs>
		<filter id="none" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0" />
		</filter>
		<filter id="protanopia" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.567 0.433 0 0 0 0.558 0.442 0 0 0 0 0.242 0.758 0 0 0 0 0 1 0" />
		</filter>
		<filter id="protanomaly" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.817 0.183 0 0 0 0.333 0.667 0 0 0 0 0.125 0.875 0 0 0 0 0 1 0" />
		</filter>
		<filter id="deuteranopia" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.625 0.375 0 0 0 0.7 0.3 0 0 0 0 0.3 0.7 0 0 0 0 0 1 0" />
		</filter>
		<filter id="deuteranomaly" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.8 0.2 0 0 0 0.258 0.742 0 0 0 0 0.142 0.858 0 0 0 0 0 1 0" />
		</filter>
		<filter id="tritanopia" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.95 0.05 0 0 0 0 0.433 0.567 0 0 0 0.475 0.525 0 0 0 0 0 1 0" />
		</filter>
		<filter id="tritanomaly" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.967 0.033 0 0 0 0 0.733 0.267 0 0 0 0.183 0.817 0 0 0 0 0 1 0" />
		</filter>
		<filter id="achromatopsia" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.299 0.587 0.114 0 0 0.299 0.587 0.114 0 0 0.299 0.587 0.114 0 0 0 0 0 1 0" />
		</filter>
		<filter id="achromatomaly" color-interpolation-filters="linearRGB">
			<feColorMatrix type="matrix" in="SourceGraphic" values="0.618 0.320 0.062 0 0 0.618 0.320 0.062 0 0 0.618 0.320 0.062 0 0 0 0 0 1 0" />
		</filter>
	</defs>
</svg>

<div class="cvd-wrapper" data-cvd-mode={currentFilter}>
	{@render children()}
</div>

<style>
	:global(*) {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(:root) {
		--bg-primary: #0a0a0b;
		--bg-secondary: #141416;
		--bg-card: #1a1a1d;
		--bg-card-hover: #222225;
		--bg-elevated: #2a2a2e;

		--text-primary: #ffffff;
		--text-secondary: #a1a1aa;
		--text-muted: #71717a;

		--accent-primary: #6366f1;
		--accent-secondary: #818cf8;
		--accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);

		--success: #22c55e;
		--error: #ef4444;
		--warning: #f59e0b;

		--border-subtle: rgba(255, 255, 255, 0.06);
		--border-light: rgba(255, 255, 255, 0.1);

		--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
		--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
		--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
		--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.5);
		--shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);

		--radius-sm: 8px;
		--radius-md: 12px;
		--radius-lg: 16px;
		--radius-xl: 24px;
		--radius-full: 9999px;

		--transition-fast: 150ms ease;
		--transition-base: 200ms ease;
		--transition-slow: 300ms ease;
		--transition-spring: 400ms cubic-bezier(0.34, 1.56, 0.64, 1);

		--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	:global(html) {
		scroll-behavior: smooth;
	}

	:global(body) {
		font-family: var(--font-sans);
		background-color: var(--bg-primary);
		color: var(--text-primary);
		line-height: 1.6;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}

	:global(::selection) {
		background-color: var(--accent-primary);
		color: white;
	}

	:global(::-webkit-scrollbar) {
		width: 10px;
		height: 10px;
	}

	:global(::-webkit-scrollbar-track) {
		background: var(--bg-secondary);
	}

	:global(::-webkit-scrollbar-thumb) {
		background: var(--bg-elevated);
		border-radius: var(--radius-full);
		border: 2px solid var(--bg-secondary);
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: var(--accent-primary);
	}

	:global(.glass) {
		background: rgba(20, 20, 22, 0.8);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
		border: 1px solid var(--border-light);
	}

	:global(.gradient-text) {
		background: var(--accent-gradient);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	:global(.btn) {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		border-radius: var(--radius-md);
		border: none;
		cursor: pointer;
		transition: all var(--transition-base);
		text-decoration: none;
		font-family: inherit;
	}

	:global(.btn-primary) {
		background: var(--accent-gradient);
		color: white;
		box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
	}

	:global(.btn-primary:hover) {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
	}

	:global(.btn-secondary) {
		background: var(--bg-card);
		color: var(--text-primary);
		border: 1px solid var(--border-light);
	}

	:global(.btn-secondary:hover) {
		background: var(--bg-card-hover);
		border-color: var(--accent-primary);
	}

	:global(.btn-ghost) {
		background: transparent;
		color: var(--text-secondary);
	}

	:global(.btn-ghost:hover) {
		background: var(--bg-card);
		color: var(--text-primary);
	}

	:global(.card) {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: 1.5rem;
		transition: all var(--transition-base);
	}

	:global(.card:hover) {
		border-color: var(--border-light);
		transform: translateY(-2px);
		box-shadow: var(--shadow-lg);
	}

	:global(.input) {
		width: 100%;
		padding: 0.875rem 1rem;
		font-size: 0.9375rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		color: var(--text-primary);
		transition: all var(--transition-fast);
		font-family: inherit;
	}

	:global(.input::placeholder) {
		color: var(--text-muted);
	}

	:global(.input:focus) {
		outline: none;
		border-color: var(--accent-primary);
		box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
	}

	:global(.fade-in) {
		animation: fadeIn 0.5s ease forwards;
	}

	:global(.slide-up) {
		animation: slideUp 0.5s ease forwards;
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

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	@keyframes float {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	@keyframes gradientShift {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}

	.svg-filters {
		position: fixed;
		width: 0;
		height: 0;
		pointer-events: none;
	}

	.cvd-wrapper {
		min-height: 100vh;
		transition: filter var(--transition-base);
	}

	.cvd-wrapper[data-cvd-mode="protanopia"] {
		filter: url('#protanopia');
	}

	.cvd-wrapper[data-cvd-mode="protanomaly"] {
		filter: url('#protanomaly');
	}

	.cvd-wrapper[data-cvd-mode="deuteranopia"] {
		filter: url('#deuteranopia');
	}

	.cvd-wrapper[data-cvd-mode="deuteranomaly"] {
		filter: url('#deuteranomaly');
	}

	.cvd-wrapper[data-cvd-mode="tritanopia"] {
		filter: url('#tritanopia');
	}

	.cvd-wrapper[data-cvd-mode="tritanomaly"] {
		filter: url('#tritanomaly');
	}

	.cvd-wrapper[data-cvd-mode="achromatopsia"] {
		filter: url('#achromatopsia');
	}

	.cvd-wrapper[data-cvd-mode="achromatomaly"] {
		filter: url('#achromatomaly');
	}
</style>
