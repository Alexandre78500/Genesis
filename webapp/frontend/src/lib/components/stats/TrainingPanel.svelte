<script lang="ts">
	import { trainingProgress, isTraining } from '$lib/stores/training';
	import ProgressBar from './ProgressBar.svelte';
</script>

{#if $isTraining && $trainingProgress}
	<div class="training-live">
		<div class="training-header">
			<span class="live-dot"></span>
			TRAINING IN PROGRESS
		</div>
		<div class="training-grid">
			<div class="metric">
				<span class="metric-val">{$trainingProgress.step}</span>
				<span class="metric-label">STEP</span>
			</div>
			<div class="metric">
				<span class="metric-val">{$trainingProgress.loss.toFixed(4)}</span>
				<span class="metric-label">LOSS</span>
			</div>
			<div class="metric">
				<span class="metric-val">{$trainingProgress.tok_per_sec}</span>
				<span class="metric-label">TOK/SEC</span>
			</div>
			<div class="metric">
				<span class="metric-val">{$trainingProgress.remaining_s}s</span>
				<span class="metric-label">REMAINING</span>
			</div>
		</div>
		<ProgressBar value={$trainingProgress.progress_pct} color="#ff9a00" />
	</div>
{:else}
	<div class="training-idle">
		<span class="idle-text">IDLE — AWAITING NEXT EXPERIMENT</span>
	</div>
{/if}

<style>
	.training-live {
		height: 100%;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.training-header {
		font-size: 0.65rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: #ff9a00;
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.live-dot {
		width: 6px;
		height: 6px;
		background: #ff9a00;
		animation: pulse-glow 1s ease-in-out infinite;
	}
	.training-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 6px;
	}
	.metric {
		background: #0d0d0d;
		border: 1px solid #3a3020;
		padding: 6px 4px;
		text-align: center;
	}
	.metric-val {
		display: block;
		font-size: 0.85rem;
		font-weight: 700;
		color: #d4c4a0;
		font-variant-numeric: tabular-nums;
	}
	.metric-label {
		display: block;
		font-size: 0.5rem;
		color: #8a8070;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		margin-top: 2px;
	}
	.training-idle {
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.idle-text {
		color: #4a4030;
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
	}
</style>
