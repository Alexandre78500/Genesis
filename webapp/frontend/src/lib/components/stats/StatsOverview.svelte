<script lang="ts">
	import { stats } from '$lib/stores/stats';
	import { formatBpb, formatPct } from '$lib/utils/format';
	import StatCard from './StatCard.svelte';
	import ProgressBar from './ProgressBar.svelte';

	let improvement = $derived(
		$stats.best_bpb && $stats.baseline_bpb && $stats.baseline_bpb > 0
			? (($stats.baseline_bpb - $stats.best_bpb) / $stats.baseline_bpb) * 100
			: 0
	);
</script>

<div class="stats-grid">
	<StatCard
		value={formatBpb($stats.best_bpb)}
		label="Best BPB"
		sub={improvement > 0 ? formatPct(improvement) : ''}
	/>
	<StatCard
		value={String($stats.total_runs)}
		label="Experiments"
		sub="✓{$stats.total_keeps} ✗{$stats.total_discards} 💥{$stats.total_crashes}"
		color="#d4c4a0"
	/>
	<StatCard
		value="{$stats.success_rate.toFixed(1)}%"
		label="Success Rate"
		color={$stats.success_rate > 30 ? '#5cb85c' : '#d9534f'}
	/>
	<StatCard
		value={String($stats.consecutive_keeps)}
		label="Streak"
		sub="max: {$stats.max_consecutive_keeps}"
		color="#ff9a00"
	/>
</div>
<div class="progress-section">
	<ProgressBar
		value={improvement}
		max={10}
		label="Total improvement"
		color="#5cb85c"
	/>
</div>

<style>
	.stats-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 6px;
	}
	.progress-section {
		margin-top: 8px;
	}
</style>
