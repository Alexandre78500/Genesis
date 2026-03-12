<script lang="ts">
	import { onMount } from 'svelte';
	import { initSSE } from '$lib/stores/sse';
	import Dashboard from '$lib/components/layout/Dashboard.svelte';

	onMount(() => {
		initSSE();
	});
</script>

<svelte:head>
	<title>Autoresearch Lab — Cockpit</title>
</svelte:head>

<Dashboard />
