<script lang="ts">
	import Panel from './Panel.svelte';
	import ConnectionStatus from '$lib/components/common/ConnectionStatus.svelte';
	import StatsOverview from '$lib/components/stats/StatsOverview.svelte';
	import BpbChart from '$lib/components/charts/BpbChart.svelte';
	import ActivityFeed from '$lib/components/feed/ActivityFeed.svelte';
	import AchievementPanel from '$lib/components/achievements/AchievementPanel.svelte';
	import TrainingPanel from '$lib/components/stats/TrainingPanel.svelte';
	import TechTree from '$lib/components/techtree/TechTree.svelte';
	import UnlockToast from '$lib/components/achievements/UnlockToast.svelte';
</script>

<UnlockToast />

<div class="dashboard">
	<header class="dashboard-header">
		<div class="header-title">
			<span class="title-glow">AUTORESEARCH LAB</span>
		</div>
		<ConnectionStatus />
	</header>

	<Panel title="Production Metrics" area="metrics">
		<StatsOverview />
	</Panel>

	<Panel title="Validation Monitor" area="chart">
		<BpbChart />
	</Panel>

	<Panel title="Activity Log" area="activity">
		<ActivityFeed />
	</Panel>

	<Panel title="Achievements" area="achieve">
		<AchievementPanel />
	</Panel>

	<Panel title="Live Training" area="training">
		<TrainingPanel />
	</Panel>

	<Panel title="Research Tree" area="techtree">
		<TechTree />
	</Panel>
</div>

<style>
	.dashboard {
		display: grid;
		grid-template-columns: 280px 1fr 300px;
		grid-template-rows: 42px 1fr 1fr;
		grid-template-areas:
			'header   header   header'
			'metrics  chart    activity'
			'achieve  training techtree';
		gap: 2px;
		height: 100vh;
		background: #0d0d0d;
		padding: 2px;
	}

	.dashboard-header {
		grid-area: header;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 16px;
		background: linear-gradient(180deg, #1a1510 0%, #0d0d0d 100%);
		border-bottom: 1px solid #3a3020;
	}

	.header-title {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.title-glow {
		font-size: 0.9rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		color: #ff9a00;
		text-shadow: 0 0 8px rgba(255, 154, 0, 0.5), 0 0 16px rgba(255, 154, 0, 0.2);
	}
</style>
