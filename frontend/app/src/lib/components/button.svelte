<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	const {
		label,
		href,
		variant = 'primary',
		size = 'md'
	} = $props<{
		label: string;
		href: string;
		variant?: 'primary' | 'secondary' | 'ghost';
		size?: 'sm' | 'md' | 'lg';
	}>();

	const variantClasses: Record<string, string> = {
		primary: 'btn-primary',
		secondary: 'btn-secondary',
		ghost: 'btn-ghost'
	};

	const sizeClasses: Record<string, string> = {
		sm: 'btn-sm',
		md: '',
		lg: 'btn-lg'
	};
</script>

<a href={resolve(href)} class="btn {variantClasses[variant]} {sizeClasses[size]}">
	{label}
</a>

<style>
	.btn-sm {
		padding: 0.5rem 1rem;
		font-size: 0.8125rem;
	}

	.btn-lg {
		padding: 1rem 2rem;
		font-size: 1rem;
	}
</style>
