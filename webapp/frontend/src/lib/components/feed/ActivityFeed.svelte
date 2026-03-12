<script lang="ts">
	import { activityFeed } from '$lib/stores/activity';
	import FeedItem from './FeedItem.svelte';

	let feedContainer: HTMLDivElement;
	let autoScroll = $state(true);

	function onScroll() {
		if (!feedContainer) return;
		autoScroll = feedContainer.scrollTop < 10;
	}

	$effect(() => {
		if ($activityFeed && autoScroll && feedContainer) {
			feedContainer.scrollTop = 0;
		}
	});
</script>

<div class="feed-scroll" bind:this={feedContainer} onscroll={onScroll}>
	{#each $activityFeed as item (item.timestamp + JSON.stringify(item.data))}
		<FeedItem {item} />
	{/each}
	{#if $activityFeed.length === 0}
		<div class="feed-empty">Awaiting experiments...</div>
	{/if}
</div>

<style>
	.feed-scroll {
		height: 100%;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.feed-empty {
		text-align: center;
		color: #6a6050;
		padding: 20px;
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
</style>
