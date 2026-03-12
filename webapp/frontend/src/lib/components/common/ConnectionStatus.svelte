<script lang="ts">
	import { connectionStatus } from '$lib/stores/sse';

	const statusMap = {
		connected: { color: '#5cb85c', label: 'CONNECTED' },
		connecting: { color: '#ff9a00', label: 'CONNECTING...' },
		disconnected: { color: '#d9534f', label: 'OFFLINE' },
	};

	let status = $derived(statusMap[$connectionStatus]);
</script>

<div class="status-indicator">
	<span class="dot" style:background={status.color}></span>
	<span class="label">{status.label}</span>
</div>

<style>
	.status-indicator {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 0.65rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: #8a8070;
	}
	.dot {
		width: 6px;
		height: 6px;
		border-radius: 0;
		box-shadow: 0 0 6px currentColor;
	}
</style>
