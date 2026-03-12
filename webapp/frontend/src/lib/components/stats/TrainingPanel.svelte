<script lang="ts">
	import ProgressBar from './ProgressBar.svelte';
	import { liveRun, trainingProgress, trainingSamples } from '$lib/stores/training';
	import { formatBpb } from '$lib/utils/format';

	const titleByStatus = {
		starting: 'BOOTING / COMPILING',
		running: 'TRAINING IN PROGRESS',
		stalled: 'WAITING FOR NEXT STEP',
		finishing: 'EVALUATING / WRITING RESULTS',
		completed: 'RUN COMPLETED',
		crashed: 'RUN CRASHED',
		idle: 'IDLE',
	} as const;

	const colorByStatus = {
		starting: '#ff9a00',
		running: '#ff9a00',
		stalled: '#ffd166',
		finishing: '#5bc0de',
		completed: '#5cb85c',
		crashed: '#d9534f',
		idle: '#4a4030',
	} as const;

	let currentStatus = $derived($liveRun.status);
	let panelColor = $derived(colorByStatus[currentStatus]);
	let panelTitle = $derived(titleByStatus[currentStatus]);
	let recentSamples = $derived($trainingSamples.slice(-3).reverse());
</script>

{#if $liveRun.status !== 'idle'}
	<div class="training-live">
		<div class="training-header" style:color={panelColor}>
			<span class="live-dot" style:background={panelColor}></span>
			{panelTitle}
		</div>
		<div class="status-copy">{$liveRun.status_message}</div>

		{#if $trainingProgress}
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
			<ProgressBar value={$trainingProgress.progress_pct} color={panelColor} />
		{:else}
			<div class="training-empty-state">
				<span>Waiting for first metrics from `run.log`...</span>
			</div>
		{/if}

		{#if recentSamples.length > 0}
			<div class="recent-steps">
				{#each recentSamples as sample}
					<div class="step-chip">
						<span class="chip-step">#{sample.step}</span>
						<span class="chip-loss">{sample.loss.toFixed(4)}</span>
					</div>
				{/each}
			</div>
		{/if}

		{#if $liveRun.last_result && ['completed', 'crashed'].includes($liveRun.status)}
			<div class="run-summary">
				<div class="summary-title">Last Result</div>
				<div class="summary-row">
					<span>{$liveRun.last_result.commit.slice(0, 7)}</span>
					<span>{formatBpb($liveRun.last_result.val_bpb)}</span>
					<span class:good={$liveRun.last_result.status === 'keep'} class:bad={$liveRun.last_result.status === 'discard' || $liveRun.last_result.status === 'crash'}>
						{$liveRun.last_result.status.toUpperCase()}
					</span>
				</div>
			</div>
		{/if}
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
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.status-copy {
		font-size: 0.65rem;
		color: #8a8070;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	.live-dot {
		width: 6px;
		height: 6px;
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
	.training-empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 72px;
		border: 1px dashed #3a3020;
		color: #8a8070;
		font-size: 0.7rem;
		padding: 8px;
		text-align: center;
	}
	.recent-steps {
		display: flex;
		gap: 6px;
		flex-wrap: wrap;
	}
	.step-chip {
		display: flex;
		gap: 6px;
		align-items: center;
		padding: 4px 6px;
		background: #14110c;
		border: 1px solid #3a3020;
		font-size: 0.6rem;
		color: #d4c4a0;
	}
	.chip-step {
		color: #ff9a00;
	}
	.chip-loss {
		font-variant-numeric: tabular-nums;
	}
	.run-summary {
		margin-top: auto;
		padding: 8px;
		border: 1px solid #3a3020;
		background: #12100c;
	}
	.summary-title {
		font-size: 0.55rem;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: #8a8070;
		margin-bottom: 4px;
	}
	.summary-row {
		display: flex;
		justify-content: space-between;
		gap: 8px;
		font-size: 0.7rem;
		color: #d4c4a0;
	}
	.good {
		color: #5cb85c;
	}
	.bad {
		color: #d9534f;
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
