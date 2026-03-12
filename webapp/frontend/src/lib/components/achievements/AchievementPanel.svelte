<script lang="ts">
	import { achievements } from '$lib/stores/achievements';
	import AchievementBadge from './AchievementBadge.svelte';
</script>

<div class="achievement-grid">
	{#each $achievements as ach (ach.id)}
		<AchievementBadge achievement={ach} />
	{/each}
	{#if $achievements.length === 0}
		<div class="empty">No achievements loaded</div>
	{/if}
</div>

<style>
	.achievement-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
		gap: 4px;
	}
	.empty {
		grid-column: 1 / -1;
		text-align: center;
		color: #6a6050;
		padding: 20px;
		font-size: 0.7rem;
	}
</style>
