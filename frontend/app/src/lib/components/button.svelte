<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	const { label, href } = $props<{
		label: string;
		href: string;
	}>();
</script>

<button
	onclick={async () => {
		await goto(resolve(href));
		resolve(href);
	}}
>
	{label}
</button>

<style>
	button {
		padding: 0.75rem 1.5rem;
		background: black;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
	}

	button:hover {
		opacity: 0.9;
	}
</style>
