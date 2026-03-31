<script lang="ts">
	import { onMount } from 'svelte';
	import { authService } from '$lib/services/auth_api';
	import { resolve } from '$app/paths';
	import Logo from '$lib/components/Logo.svelte';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import { t } from '$lib/stores/locale';

	let user = $state<{ forename: string; surname?: string } | null>(null);
	let showDropdown = $state(false);
	let scrolled = $state(false);

	onMount(async () => {
		const token = localStorage.getItem('token');
		if (token) {
			try {
				const userData = await authService.getCurrentUser(token);
				user = userData;
			} catch {
				localStorage.removeItem('token');
			}
		}

		const handleScroll = () => {
			scrolled = window.scrollY > 50;
		};
		window.addEventListener('scroll', handleScroll);
		return () => window.removeEventListener('scroll', handleScroll);
	});

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	async function logout() {
		await authService.logout();
		localStorage.removeItem('token');
		user = null;
		showDropdown = false;
	}

	function handleWindowClick(e: MouseEvent) {
		const target = e.target as HTMLElement;
		if (!target.closest('.profile-wrapper')) {
			showDropdown = false;
		}
	}

	const featureKeys = [
		{ key: 'realtimeData', desc: 'realtimeDataDesc' },
		{ key: 'smartMapping', desc: 'smartMappingDesc' },
		{ key: 'securePrivate', desc: 'securePrivateDesc' }
	] as const;
</script>

<svelte:window onclick={handleWindowClick} />

<main>
	<nav class="navbar" class:scrolled>
		<a href={resolve('/')} class="navbar-logo">
			<Logo size={32} />
			<span>Tanker24</span>
		</a>

		<div class="nav-actions">
			<LanguageSwitcher />
			<a href={resolve('/map')} class="btn btn-ghost nav-link">{$t.nav.map}</a>
			{#if user}
				<div class="profile-wrapper">
					<button class="profile-btn" onclick={toggleDropdown}>
						<span class="avatar">
							{user.forename[0]}{user.surname?.[0] || ''}
						</span>
						<span class="username">{user.forename}</span>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M6 9l6 6 6-6" />
						</svg>
					</button>
					{#if showDropdown}
						<div class="dropdown">
							<a href={resolve('/account')} class="dropdown-item">
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
									<circle cx="12" cy="7" r="4" />
								</svg>
								{$t.nav.account}
							</a>
							<button class="dropdown-item logout" onclick={logout}>
								<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
									<polyline points="16,17 21,12 16,7" />
									<line x1="21" y1="12" x2="9" y2="12" />
								</svg>
								{$t.nav.logout}
							</button>
						</div>
					{/if}
				</div>
			{:else}
				<a href={resolve('/login')} class="btn btn-secondary">{$t.nav.signIn}</a>
				<a href={resolve('/register')} class="btn btn-primary">{$t.nav.getStarted}</a>
			{/if}
		</div>
	</nav>

	<section class="hero">
		<div class="hero-bg">
			<div class="gradient-orb orb-1"></div>
			<div class="gradient-orb orb-2"></div>
			<div class="grid-pattern"></div>
		</div>
		<div class="hero-content">
			<div class="badge">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
				</svg>
				{$t.hero.badge}
			</div>
			<h1>
				{$t.hero.title}
			</h1>
			<p class="hero-subtitle">{$t.hero.subtitle}</p>
			<div class="hero-actions">
				<a href={resolve('/map')} class="btn btn-primary btn-lg">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
						<line x1="9" y1="3" x2="9" y2="18" />
						<line x1="15" y1="6" x2="15" y2="21" />
					</svg>
					{$t.hero.exploreMap}
				</a>
				<a href={resolve('/register')} class="btn btn-secondary btn-lg">{$t.hero.createAccount}</a>
			</div>
			<div class="stats">
				<div class="stat">
					<span class="stat-value">500+</span>
					<span class="stat-label">{$t.hero.fuelStationsLabel}</span>
				</div>
				<div class="stat-divider"></div>
				<div class="stat">
					<span class="stat-value">{$t.hero.priceUpdatesLabel}</span>
				</div>
				<div class="stat-divider"></div>
			</div>
			<p class="data-source">{$t.hero.dataSource}</p>
		</div>
	</section>

	<section class="features">
		<div class="section-header">
			<span class="section-badge">{$t.features.title}</span>
			<h2>{$t.features.subtitle}</h2>
			<p>{$t.features.description}</p>
		</div>
		<div class="features-grid">
			{#each featureKeys as { key, desc }, i (key)}
				<div class="feature-card page-card" style="animation-delay: {i * 100}ms">
					<div class="feature-icon">
						{#if key === 'realtimeData'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
							</svg>
						{:else if key === 'smartMapping'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
								<circle cx="12" cy="10" r="3" />
							</svg>
						{:else if key === 'securePrivate'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
							</svg>
						{/if}
					</div>
					<h3>{$t.features[key]}</h3>
					<p>{$t.features[desc]}</p>
				</div>
			{/each}
		</div>
	</section>

	<section class="cta">
		<div class="cta-content page-card">
			<h2>{$t.cta.title}</h2>
			<p>{$t.cta.subtitle}</p>
			<a href={resolve('/register')} class="btn btn-primary btn-lg">{$t.cta.getStartedFree}</a>
		</div>
	</section>

	<footer class="footer">
		<div class="footer-content">
			<div class="footer-brand">
				<div class="navbar-logo">
					<Logo size={28} />
					<span>Tanker24</span>
				</div>
				<p>{$t.footer.brand}</p>
			</div>
			<div class="footer-links">
				<div class="footer-column">
					<h4>{$t.footer.product}</h4>
					<a href={resolve('/map')}>{$t.footer.map}</a>
					<a href={resolve('/register')}>{$t.footer.signUp}</a>
					<a href={resolve('/login')}>{$t.footer.signIn}</a>
				</div>
				<div class="footer-column">
					<h4>{$t.footer.company}</h4>
					<a href={resolve('/')}>{$t.footer.about}</a>
					<a href={resolve('/')}>{$t.footer.contact}</a>
					<a href={resolve('/')}>{$t.footer.privacy}</a>
				</div>
			</div>
		</div>
		<div class="footer-bottom">
			<p>&copy; {$t.footer.copyright}</p>
		</div>
	</footer>
</main>

<style>
	main {
		min-height: 100vh;
	}

	.navbar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		padding: 1rem 2rem;
		max-width: 1200px;
		margin: 0 auto;
		width: 100%;
		box-sizing: border-box;
		display: flex;
		align-items: center;
		justify-content: space-between;
		transition: all var(--transition-base);
	}

	.navbar.scrolled {
		background: rgba(10, 10, 11, 0.9);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}

	.nav-actions {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.nav-link {
		padding: 0.5rem 1rem;
		font-weight: 500;
	}

	.username {
		display: none;
	}

	@media (min-width: 640px) {
		.username {
			display: inline;
		}
	}

	.hero {
		position: relative;
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 8rem 2rem 4rem;
		overflow: hidden;
	}

	.hero-bg {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	.hero-content {
		position: relative;
		max-width: 900px;
		text-align: center;
		animation: slideUp 0.8s ease forwards;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: rgba(99, 102, 241, 0.1);
		border: 1px solid rgba(99, 102, 241, 0.3);
		border-radius: var(--radius-full);
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--accent-secondary);
		margin-bottom: 2rem;
	}

	.hero h1 {
		font-size: clamp(2.5rem, 6vw, 4.5rem);
		font-weight: 800;
		line-height: 1.1;
		margin-bottom: 1.5rem;
		letter-spacing: -0.02em;
	}

	.hero-subtitle {
		font-size: clamp(1.125rem, 2vw, 1.375rem);
		color: var(--text-secondary);
		max-width: 600px;
		margin: 0 auto 2.5rem;
		line-height: 1.7;
	}

	.hero-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
		margin-bottom: 4rem;
	}

	.stats {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 2rem;
		flex-wrap: wrap;
	}

	.stat {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.stat-label {
		font-size: 0.875rem;
		color: var(--text-muted);
	}

	.stat-divider {
		width: 1px;
		height: 40px;
		background: var(--border-light);
	}

	.data-source {
		margin-top: 1.5rem;
		font-size: 0.75rem;
		color: var(--text-muted);
		text-align: center;
	}

	.features {
		padding: 6rem 2rem;
		max-width: 1200px;
		margin: 0 auto;
	}

	.section-header {
		text-align: center;
		margin-bottom: 4rem;
	}

	.section-badge {
		display: inline-block;
		padding: 0.375rem 0.875rem;
		background: rgba(99, 102, 241, 0.1);
		border: 1px solid rgba(99, 102, 241, 0.2);
		border-radius: var(--radius-full);
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--accent-secondary);
		margin-bottom: 1rem;
	}

	.section-header h2 {
		font-size: clamp(2rem, 4vw, 3rem);
		font-weight: 700;
		margin-bottom: 1rem;
		letter-spacing: -0.02em;
	}

	.section-header p {
		font-size: 1.125rem;
		color: var(--text-secondary);
	}

	.features-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
	}

	.feature-card {
		animation: slideUp 0.6s ease forwards;
		opacity: 0;
	}

	.feature-card:hover {
		border-color: var(--accent-primary);
		transform: translateY(-4px);
		box-shadow: var(--shadow-glow);
	}

	.feature-icon {
		width: 48px;
		height: 48px;
		border-radius: var(--radius-md);
		background: rgba(99, 102, 241, 0.1);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--accent-primary);
		margin-bottom: 1.5rem;
	}

	.feature-card h3 {
		font-size: 1.25rem;
		font-weight: 600;
		margin-bottom: 0.75rem;
	}

	.feature-card p {
		color: var(--text-secondary);
		line-height: 1.6;
	}

	.cta {
		padding: 6rem 2rem;
		position: relative;
		overflow: hidden;
	}

	.cta::before {
		content: '';
		position: absolute;
		inset: 0;
		background: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
	}

	.cta-content {
		position: relative;
		max-width: 600px;
		margin: 0 auto;
		text-align: center;
		padding: 4rem 2rem;
	}

	.cta-content h2 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 0.75rem;
	}

	.cta-content p {
		color: var(--text-secondary);
		margin-bottom: 2rem;
		font-size: 1.125rem;
	}

	.footer {
		border-top: 1px solid var(--border-subtle);
		padding: 4rem 2rem 2rem;
	}

	.footer-content {
		max-width: 1200px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr;
		gap: 3rem;
	}

	@media (min-width: 768px) {
		.footer-content {
			grid-template-columns: 2fr 1fr;
		}
	}

	.footer-brand {
		max-width: 300px;
	}

	.footer-brand .navbar-logo {
		margin-bottom: 1rem;
	}

	.footer-brand p {
		color: var(--text-secondary);
		font-size: 0.875rem;
		line-height: 1.6;
	}

	.footer-links {
		display: flex;
		gap: 4rem;
	}

	.footer-column {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.footer-column h4 {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
		margin-bottom: 0.25rem;
	}

	.footer-column a {
		color: var(--text-secondary);
		text-decoration: none;
		font-size: 0.875rem;
		transition: color var(--transition-fast);
	}

	.footer-column a:hover {
		color: var(--text-primary);
	}

	.footer-bottom {
		max-width: 1200px;
		margin: 3rem auto 0;
		padding-top: 2rem;
		border-top: 1px solid var(--border-subtle);
		text-align: center;
	}

	.footer-bottom p {
		color: var(--text-muted);
		font-size: 0.875rem;
	}
</style>
