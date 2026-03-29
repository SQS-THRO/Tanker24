<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { createWebSocketService, type StationMessage, type ConnectionStatus } from '$lib/services/websocket';
	import { t, locale } from '$lib/stores/locale';

	interface Props {
		lat: number;
		lon: number;
	}

	let { lat, lon }: Props = $props();

	let messages: StationMessage[] = $state([]);
	let status: ConnectionStatus = $state('disconnected');
	let wsService: ReturnType<typeof createWebSocketService> | null = $state(null);
	let messagesContainer: HTMLDivElement;

	function formatMessage(message: StationMessage): string {
		switch (message.type) {
			case 'caching_stations':
				return `${$t.ws.cachingStations} ${message.lat.toFixed(4)} ${message.lon.toFixed(4)}`;
			case 'new_station':
				return `${$t.ws.newStation}: ${message.name} (${message.brand}) ${$t.ws.at} ${message.lat.toFixed(4)} ${message.lon.toFixed(4)}`;
			case 'updated_station':
				return `${$t.ws.updatedStation}: ${message.name} (${message.brand}) ${$t.ws.at} ${message.lat.toFixed(4)} ${message.lon.toFixed(4)}`;
			case 'error':
				return `${$t.ws.error}: ${message.message}`;
			case 'complete':
				return `Complete: ${message.lat.toFixed(4)} ${message.lon.toFixed(4)}`;
			default:
				return JSON.stringify(message);
		}
	}

	function getMessageIcon(message: StationMessage): string {
		switch (message.type) {
			case 'caching_stations':
				return 'loading';
			case 'new_station':
				return 'new';
			case 'updated_station':
				return 'updated';
			case 'error':
				return 'error';
			case 'complete':
				return 'complete';
			default:
				return 'default';
		}
	}

	onMount(() => {
		wsService = createWebSocketService();

		wsService.onMessage((message: StationMessage) => {
			messages = [message, ...messages].slice(0, 50);
			setTimeout(() => {
				if (messagesContainer) {
					messagesContainer.scrollTop = 0;
				}
			}, 10);
		});

		wsService.onStatusChange((newStatus) => {
			status = newStatus;
		});

		wsService.subscribe(lat, lon);
	});

	onDestroy(() => {
		if (wsService) {
			wsService.disconnect();
		}
	});

	$effect(() => {
		if (wsService && lat && lon) {
			wsService.subscribe(lat, lon);
		}
	});
</script>

<div class="station-feed glass">
	<div class="feed-header">
		<div class="feed-title">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
				<polyline points="22,6 12,13 2,6" />
			</svg>
			<span>{$t.ws.liveUpdates}</span>
		</div>
		<div class="status-badge" class:connected={status === 'connected'} class:connecting={status === 'connecting'}>
			{#if status === 'connecting'}
				<span class="status-dot connecting"></span>
				{$t.ws.connecting}
			{:else if status === 'connected'}
				<span class="status-dot connected"></span>
				{$t.ws.connected}
			{:else}
				<span class="status-dot disconnected"></span>
				{$t.ws.disconnected}
			{/if}
		</div>
	</div>

	<div class="feed-messages" bind:this={messagesContainer}>
		{#if messages.length === 0}
			<div class="empty-state">
				<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
					<circle cx="12" cy="12" r="10" />
					<polyline points="12 6 12 12 16 14" />
				</svg>
				<p>Waiting for updates...</p>
			</div>
		{:else}
			{#each messages as message, index (index)}
				<div class="message-item {message.type}" style="animation-delay: {index * 50}ms">
					<div class="message-icon">
						{#if message.type === 'caching_stations'}
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								<path d="M12 6v6l4 2" />
							</svg>
						{:else if message.type === 'new_station'}
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M12 5v14M5 12h14" />
							</svg>
						{:else if message.type === 'updated_station'}
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M17 1l4 4-4 4" />
								<path d="M3 11V9a4 4 0 014-4h14" />
								<path d="M7 23l-4-4 4-4" />
								<path d="M21 13v2a4 4 0 01-4 4H3" />
							</svg>
						{:else if message.type === 'error'}
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="12" cy="12" r="10" />
								<line x1="15" y1="9" x2="9" y2="15" />
								<line x1="9" y1="9" x2="15" y2="15" />
							</svg>
						{:else}
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<polyline points="20 6 9 17 4 12" />
							</svg>
						{/if}
					</div>
					<span class="message-text">{formatMessage(message)}</span>
				</div>
			{/each}
		{/if}
	</div>
</div>

<style>
	.station-feed {
		position: absolute;
		top: 5.5rem;
		right: 1rem;
		width: 320px;
		max-height: calc(100vh - 8rem);
		z-index: 1000;
		display: flex;
		flex-direction: column;
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.feed-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--border-subtle);
		background: var(--bg-card);
	}

	.feed-title {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.status-badge {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		font-size: 0.75rem;
		padding: 0.25rem 0.5rem;
		border-radius: var(--radius-full);
		background: var(--bg-secondary);
		color: var(--text-muted);
	}

	.status-badge.connected {
		background: rgba(34, 197, 94, 0.15);
		color: #22c55e;
	}

	.status-badge.connecting {
		background: rgba(251, 191, 36, 0.15);
		color: #fbbf24;
	}

	.status-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: currentColor;
	}

	.status-dot.connecting {
		animation: pulse 1s ease-in-out infinite;
	}

	.status-dot.connected {
		animation: pulse 2s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	.feed-messages {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
		background: var(--bg-card);
		max-height: 400px;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		color: var(--text-muted);
		text-align: center;
		gap: 0.75rem;
	}

	.empty-state svg {
		opacity: 0.5;
	}

	.empty-state p {
		font-size: 0.8125rem;
	}

	.message-item {
		display: flex;
		align-items: flex-start;
		gap: 0.625rem;
		padding: 0.625rem 0.75rem;
		margin-bottom: 0.375rem;
		border-radius: var(--radius-md);
		background: var(--bg-secondary);
		font-size: 0.8125rem;
		animation: slideIn 0.2s ease forwards;
		opacity: 0;
		transform: translateX(10px);
	}

	@keyframes slideIn {
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	.message-icon {
		flex-shrink: 0;
		width: 20px;
		height: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
	}

	.message-item.caching_stations .message-icon {
		color: #fbbf24;
	}

	.message-item.new_station .message-icon {
		color: #22c55e;
		background: rgba(34, 197, 94, 0.15);
	}

	.message-item.updated_station .message-icon {
		color: #3b82f6;
		background: rgba(59, 130, 246, 0.15);
	}

	.message-item.error .message-icon {
		color: #ef4444;
		background: rgba(239, 68, 68, 0.15);
	}

	.message-item.complete .message-icon {
		color: #22c55e;
	}

	.message-text {
		color: var(--text-secondary);
		line-height: 1.4;
		word-break: break-word;
	}

	@media (max-width: 640px) {
		.station-feed {
			width: calc(100% - 2rem);
			right: 1rem;
			left: 1rem;
			max-height: 200px;
		}
	}
</style>
