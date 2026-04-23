<script lang="ts">
	import { resolve } from '$app/paths';
	import Logo from '$lib/components/Logo.svelte';
	import { t } from '$lib/stores/locale';
</script>

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
