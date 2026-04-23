<script lang="ts">
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
