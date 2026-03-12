<script lang="ts">
	interface Props {
		value: string;
		label: string;
		sub?: string;
		color?: string;
	}
	let { value, label, sub = '', color = '#ff9a00' }: Props = $props();
</script>

<div class="stat-card">
	<div class="stat-value" style:color style:text-shadow="0 0 6px {color}40">
		{value}
	</div>
	<div class="stat-label">{label}</div>
	{#if sub}
		<div class="stat-sub">{sub}</div>
	{/if}
</div>

<style>
	.stat-card {
		background: #0d0d0d;
		border: 1px solid #3a3020;
		padding: 10px 8px;
		text-align: center;
	}
	.stat-value {
		font-size: 1.3rem;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
	}
	.stat-label {
		font-size: 0.6rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: #8a8070;
		margin-top: 4px;
	}
	.stat-sub {
		font-size: 0.6rem;
		color: #6a6050;
		margin-top: 2px;
	}
</style>
