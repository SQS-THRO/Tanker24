<script lang="ts">
	import { resolve } from '$app/paths';
	import Navbar from '$lib/components/Navbar.svelte';
	import Logo from '$lib/components/Logo.svelte';
	import { t } from '$lib/stores/locale';

	const featureKeys = [
		{ key: 'realtimeData', desc: 'realtimeDataDesc' },
		{ key: 'smartMapping', desc: 'smartMappingDesc' },
		{ key: 'securePrivate', desc: 'securePrivateDesc' }
	] as const;
</script>

<main>
	<Navbar />

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
					<a href={resolve('/impressum')}>{$t.footer.impressum}</a>
					<a href={resolve('/privacy')}>{$t.footer.privacy}</a>
				</div>
			</div>
		</div>
		<div class="footer-bottom">
			<p>&copy; {$t.footer.copyright}</p>
		</div>
	</footer>
</main>
