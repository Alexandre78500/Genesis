<script lang="ts">
	import type { Achievement } from '$lib/stores/achievements';
	import { tierColors } from '$lib/theme/factorio';

	interface Props {
		achievement: Achievement;
	}
	let { achievement }: Props = $props();

	let color = $derived(
		achievement.unlocked
			? tierColors[achievement.tier] || '#8a8070'
			: '#2a2015'
	);
</script>

<div
	class="badge"
	class:unlocked={achievement.unlocked}
	style:border-color={achievement.unlocked ? color : '#3a3020'}
	style:box-shadow={achievement.unlocked ? `0 0 8px ${color}40` : 'none'}
	title="{achievement.name}: {achievement.description}"
>
	<span class="badge-icon" class:locked={!achievement.unlocked}>
		{achievement.unlocked ? achievement.icon : '🔒'}
	</span>
	<span class="badge-name" style:color={achievement.unlocked ? color : '#4a4030'}>
		{achievement.name}
	</span>
</div>

<style>
	.badge {
		background: #0d0d0d;
		border: 1px solid #3a3020;
		padding: 6px 4px;
		text-align: center;
		cursor: default;
		transition: box-shadow 0.3s;
	}
	.badge.unlocked:hover {
		border-color: #5a4a30;
	}
	.badge-icon {
		font-size: 1.2rem;
		display: block;
	}
	.badge-icon.locked {
		opacity: 0.3;
		filter: grayscale(1);
	}
	.badge-name {
		font-size: 0.5rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		display: block;
		margin-top: 2px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>
