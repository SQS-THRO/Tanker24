<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import faviconDark from '$lib/assets/favicon-dark.svg';
	import { themeStore, CVD_PALETTES, THEME_PALETTES } from '$lib/stores/theme';
	import { onMount } from 'svelte';

	let { children } = $props();

	function applyThemeVariables(override: keyof typeof CVD_PALETTES) {
		if (typeof document === 'undefined') return;

		const globalTheme = $themeStore.globalTheme;
		const basePalette = THEME_PALETTES[globalTheme];
		const cvdPalette = CVD_PALETTES[override];
		const root = document.documentElement;

		root.style.setProperty('--bg-primary', basePalette.bgPrimary);
		root.style.setProperty('--bg-secondary', basePalette.bgSecondary);
		root.style.setProperty('--bg-card', basePalette.bgCard);
		root.style.setProperty('--bg-card-hover', basePalette.bgCardHover);
		root.style.setProperty('--bg-elevated', basePalette.bgElevated);
		root.style.setProperty('--text-primary', basePalette.textPrimary);
		root.style.setProperty('--text-secondary', basePalette.textSecondary);
		root.style.setProperty('--text-muted', basePalette.textMuted);

		const accentSource = cvdPalette || basePalette;
		root.style.setProperty('--accent-primary', accentSource.accentPrimary);
		root.style.setProperty('--accent-secondary', accentSource.accentSecondary);
		root.style.setProperty('--accent-gradient', accentSource.accentGradient);
		root.style.setProperty('--success', accentSource.success);
		root.style.setProperty('--error', accentSource.error);
		root.style.setProperty('--warning', accentSource.warning);

		if (globalTheme === 'light-modern') {
			document.body.classList.add('light-theme');
		} else {
			document.body.classList.remove('light-theme');
		}
	}

	onMount(() => {
		const stored = localStorage.getItem('theme-settings');
		let override: keyof typeof CVD_PALETTES = 'none';
		if (stored) {
			try {
				const settings = JSON.parse(stored);
				override = settings.colorBlindOverride || 'none';
			} catch {
				override = 'none';
			}
		}
		applyThemeVariables(override);
	});

	$effect(() => {
		applyThemeVariables($themeStore.colorBlindOverride);
	});
</script>

<svelte:head>
	<link rel="icon" href={$themeStore.globalTheme === 'dark-modern' ? faviconDark : favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
	<title>Tanker24</title>
</svelte:head>

{@render children()}

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

	:global(body.light-theme .glass) {
		background: rgba(250, 250, 250, 0.8);
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

	:global(.background) {
		position: fixed;
		inset: 0;
		pointer-events: none;
		z-index: 0;
	}

	:global(.gradient-orb) {
		position: absolute;
		border-radius: 50%;
		filter: blur(100px);
	}

	:global(.orb-1) {
		width: 500px;
		height: 500px;
		background: var(--accent-primary);
		top: -150px;
		right: -100px;
		opacity: 0.12;
	}

	:global(.orb-2) {
		width: 400px;
		height: 400px;
		background: #8b5cf6;
		bottom: -100px;
		left: -100px;
		opacity: 0.08;
	}

	:global(.grid-pattern) {
		position: absolute;
		inset: 0;
		background-image: linear-gradient(var(--border-subtle) 1px, transparent 1px), linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
		background-size: 60px 60px;
		mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
		-webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
	}

	:global(.navbar) {
		position: relative;
		z-index: 100;
		padding: 1.5rem 2rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
		box-sizing: border-box;
	}

	:global(.navbar-logo) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		text-decoration: none;
		color: var(--text-primary);
		font-weight: 700;
		font-size: 1.25rem;
	}

	:global(.container) {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		position: relative;
		z-index: 10;
	}

	:global(.auth-card) {
		width: 100%;
		max-width: 460px;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-xl);
		padding: 2.5rem;
		animation: slideUp 0.5s ease forwards;
	}

	:global(.card-header) {
		text-align: center;
		margin-bottom: 2rem;
	}

	:global(.card-header h1) {
		font-size: 1.75rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	:global(.card-header p) {
		color: var(--text-secondary);
	}

	:global(.error-alert) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.875rem 1rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: var(--radius-md);
		color: #fca5a5;
		font-size: 0.875rem;
		margin-bottom: 1.5rem;
	}

	:global(.form-group) {
		margin-bottom: 1.25rem;
	}

	:global(.form-group label) {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}

	:global(.form-row) {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	:global(.input-wrapper) {
		position: relative;
	}

	:global(.input-icon) {
		position: absolute;
		left: 1rem;
		top: 50%;
		transform: translateY(-50%);
		color: var(--text-muted);
		pointer-events: none;
	}

	:global(.input.with-icon) {
		padding-left: 2.75rem;
	}

	:global(.toggle-password) {
		position: absolute;
		right: 0.75rem;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		color: var(--text-muted);
		cursor: pointer;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color var(--transition-fast);
	}

	:global(.toggle-password:hover) {
		color: var(--text-primary);
	}

	:global(.submit-btn) {
		width: 100%;
		padding: 0.875rem;
		font-size: 1rem;
		margin-top: 0.5rem;
	}

	:global(.submit-btn:disabled) {
		opacity: 0.7;
		cursor: not-allowed;
	}

	:global(.spinner) {
		width: 18px;
		height: 18px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	:global(.spinner-large) {
		width: 40px;
		height: 40px;
		border: 3px solid var(--border-light);
		border-top-color: var(--accent-primary);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	:global(.divider) {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin: 1.5rem 0;
		color: var(--text-muted);
		font-size: 0.875rem;
	}

	:global(.divider::before),
	:global(.divider::after) {
		content: '';
		flex: 1;
		height: 1px;
		background: var(--border-light);
	}

	:global(.footer-text) {
		text-align: center;
		color: var(--text-secondary);
		font-size: 0.9375rem;
	}

	:global(.footer-text a) {
		color: var(--accent-secondary);
		font-weight: 500;
		text-decoration: none;
		transition: color var(--transition-fast);
	}

	:global(.footer-text a:hover) {
		color: var(--accent-primary);
	}

	:global(.profile-wrapper) {
		position: relative;
	}

	:global(.profile-btn),
	:global(.user-btn) {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-full);
		color: var(--text-primary);
		cursor: pointer;
		transition: all var(--transition-base);
		font-family: inherit;
		font-size: 0.875rem;
		font-weight: 500;
	}

	:global(.profile-btn:hover),
	:global(.user-btn:hover) {
		background: var(--bg-card-hover);
		border-color: var(--accent-primary);
	}

	:global(.avatar),
	:global(.user-avatar) {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: var(--accent-gradient);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	:global(.avatar-large) {
		width: 100px;
		height: 100px;
		border-radius: 50%;
		background: var(--accent-gradient);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2.5rem;
		font-weight: 700;
		text-transform: uppercase;
		margin: 0 auto 1.5rem;
		box-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
	}

	:global(.dropdown) {
		position: absolute;
		top: calc(100% + 0.5rem);
		right: 0;
		background: var(--bg-card);
		border: 1px solid var(--border-light);
		border-radius: var(--radius-md);
		padding: 0.5rem;
		min-width: 180px;
		box-shadow: var(--shadow-xl);
		animation: fadeIn 0.15s ease;
	}

	:global(.dropdown-header) {
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid var(--border-subtle);
		margin-bottom: 0.25rem;
	}

	:global(.dropdown-name) {
		font-size: 0.875rem;
		font-weight: 600;
	}

	:global(.dropdown-item) {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		width: 100%;
		padding: 0.75rem 1rem;
		border: none;
		background: none;
		color: var(--text-secondary);
		font-size: 0.875rem;
		font-weight: 500;
		border-radius: var(--radius-sm);
		cursor: pointer;
		transition: all var(--transition-fast);
		text-decoration: none;
		font-family: inherit;
	}

	:global(.dropdown-item:hover) {
		background: var(--bg-card-hover);
		color: var(--text-primary);
	}

	:global(.dropdown-item.logout:hover) {
		background: rgba(239, 68, 68, 0.1);
		color: var(--error);
	}

	:global(.page-card) {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: 1.5rem;
		transition: all var(--transition-base);
	}

	:global(.page-card:hover) {
		border-color: var(--border-light);
		transform: translateY(-2px);
		box-shadow: var(--shadow-lg);
	}

	:global(.btn-sm) {
		padding: 0.5rem 1rem;
		font-size: 0.8125rem;
	}

	:global(.btn-lg) {
		padding: 1rem 2rem;
		font-size: 1rem;
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

	:global(.input.input-error) {
		border-color: var(--error);
	}

	:global(.input.input-error:focus) {
		box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
	}

	:global(.input.input-success) {
		border-color: var(--success);
	}

	:global(.input.input-success:focus) {
		box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.15);
	}

	:global(.validation-icon) {
		position: absolute;
		right: 2.5rem;
		top: 50%;
		transform: translateY(-50%);
	}

	:global(.validation-icon.valid) {
		color: var(--success);
	}

	:global(.validation-icon.invalid) {
		color: var(--error);
	}

	:global(.validation-text) {
		font-size: 0.75rem;
		margin-top: 0.375rem;
	}

	:global(.validation-text.error) {
		color: var(--error);
	}

	:global(.password-checklist) {
		margin-top: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	:global(.checklist-item) {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	:global(.checklist-item.valid) {
		color: var(--success);
	}

	:global(.checklist-item svg) {
		flex-shrink: 0;
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
</style>
