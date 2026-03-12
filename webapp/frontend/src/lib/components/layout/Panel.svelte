<script lang="ts">
	interface Props {
		title: string;
		area?: string;
		children: import('svelte').Snippet;
	}
	let { title, area = '', children }: Props = $props();
</script>

<div class="panel" style:grid-area={area || undefined}>
	<div class="panel-header">
		{title}
	</div>
	<div class="panel-content">
		{@render children()}
	</div>
</div>

<style>
	.panel {
		background: #1a1510;
		border: 2px solid #3a3020;
		box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5), 0 0 8px rgba(255, 154, 0, 0.05);
		display: flex;
		flex-direction: column;
		overflow: hidden;
		min-height: 0;
	}
	.panel-header {
		background: linear-gradient(180deg, #2a2015 0%, #1a1510 100%);
		border-bottom: 1px solid #3a3020;
		padding: 6px 12px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-size: 0.7rem;
		font-weight: 700;
		color: #ff9a00;
		flex-shrink: 0;
	}
	.panel-content {
		flex: 1;
		overflow: auto;
		padding: 8px;
		min-height: 0;
	}
</style>
