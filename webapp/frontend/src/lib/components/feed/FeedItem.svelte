<script lang="ts">
	import type { ActivityItem } from '$lib/stores/activity';
	import { statusConfig } from '$lib/theme/factorio';
	import { formatBpb } from '$lib/utils/format';

	interface Props {
		item: ActivityItem;
	}
	let { item }: Props = $props();

	let borderColor = $derived(
		item.type === 'achievement'
			? '#FFD700'
			: item.type === 'experiment' && typeof item.data === 'object' && 'status' in item.data
				? statusConfig[item.data.status as keyof typeof statusConfig]?.color || '#3a3020'
				: '#3a3020'
	);
</script>

<div class="feed-item animate-fade-in" style:border-left-color={borderColor}>
	{#if item.type === 'experiment' && typeof item.data === 'object' && 'status' in item.data}
		{@const exp = item.data as any}
		<div class="feed-header">
			<span class="feed-icon" style:color={statusConfig[exp.status as keyof typeof statusConfig]?.color}>
				{statusConfig[exp.status as keyof typeof statusConfig]?.icon || '?'}
			</span>
			<span class="feed-bpb">{formatBpb(exp.val_bpb)}</span>
			<span class="feed-commit">{exp.commit?.slice(0, 7)}</span>
		</div>
		<div class="feed-desc">{exp.description}</div>
	{:else if item.type === 'achievement' && typeof item.data === 'object' && 'name' in item.data}
		{@const ach = item.data as any}
		<div class="feed-header achievement">
			<span class="feed-icon">{ach.icon}</span>
			<span class="feed-ach-name">{ach.name}</span>
		</div>
		<div class="feed-desc">{ach.description}</div>
	{:else}
		<div class="feed-desc">{String(item.data)}</div>
	{/if}
</div>

<style>
	.feed-item {
		border-left: 3px solid #3a3020;
		padding: 6px 8px;
		margin-bottom: 4px;
		background: rgba(0, 0, 0, 0.2);
	}
	.feed-header {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 0.75rem;
	}
	.feed-header.achievement {
		color: #FFD700;
	}
	.feed-icon {
		font-size: 0.8rem;
	}
	.feed-bpb {
		font-variant-numeric: tabular-nums;
		color: #d4c4a0;
	}
	.feed-commit {
		color: #6a6050;
		font-size: 0.65rem;
	}
	.feed-ach-name {
		font-weight: 700;
	}
	.feed-desc {
		font-size: 0.65rem;
		color: #8a8070;
		margin-top: 2px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>
