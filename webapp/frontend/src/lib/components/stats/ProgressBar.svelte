<script lang="ts">
	interface Props {
		value: number;
		max?: number;
		label?: string;
		color?: string;
	}
	let { value, max = 100, label = '', color = '#5cb85c' }: Props = $props();
	let pct = $derived(Math.min((value / max) * 100, 100));
</script>

<div class="progress-container">
	{#if label}
		<div class="progress-label">{label}</div>
	{/if}
	<div class="progress-track">
		<div
			class="progress-fill"
			style:width="{pct}%"
			style:background="linear-gradient(90deg, {color} 0%, {color}cc 50%, {color} 100%)"
			style:box-shadow="0 0 6px {color}66"
		></div>
	</div>
</div>

<style>
	.progress-container {
		width: 100%;
	}
	.progress-label {
		font-size: 0.6rem;
		color: #8a8070;
		margin-bottom: 3px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
	.progress-track {
		background: #0d0d0d;
		border: 1px solid #3a3020;
		height: 14px;
		overflow: hidden;
	}
	.progress-fill {
		height: 100%;
		transition: width 0.5s ease;
		background-image: repeating-linear-gradient(
			-45deg,
			transparent,
			transparent 4px,
			rgba(255, 255, 255, 0.05) 4px,
			rgba(255, 255, 255, 0.05) 8px
		);
		background-size: 20px 14px;
		animation: progress-stripe 0.5s linear infinite;
	}
</style>
