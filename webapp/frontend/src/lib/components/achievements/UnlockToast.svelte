<script lang="ts">
	import { newlyUnlocked } from '$lib/stores/achievements';
	import { tierColors } from '$lib/theme/factorio';
</script>

{#if $newlyUnlocked}
	{@const color = tierColors[$newlyUnlocked.tier] || '#FFD700'}
	<div class="toast-overlay">
		<div class="toast" style:border-color={color} style:box-shadow="0 0 20px {color}40">
			<span class="toast-icon">{$newlyUnlocked.icon}</span>
			<div class="toast-content">
				<div class="toast-title">ACHIEVEMENT UNLOCKED</div>
				<div class="toast-name" style:color>{$newlyUnlocked.name}</div>
				<div class="toast-desc">{$newlyUnlocked.description}</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.toast-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		display: flex;
		justify-content: center;
		padding: 12px;
		animation: slide-down 0.4s ease-out;
	}
	.toast {
		background: #1a1510;
		border: 2px solid #FFD700;
		padding: 12px 24px;
		display: flex;
		align-items: center;
		gap: 16px;
		max-width: 500px;
	}
	.toast-icon {
		font-size: 2rem;
	}
	.toast-title {
		font-size: 0.6rem;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		color: #8a8070;
	}
	.toast-name {
		font-size: 1.1rem;
		font-weight: 700;
		text-shadow: 0 0 8px currentColor;
	}
	.toast-desc {
		font-size: 0.7rem;
		color: #d4c4a0;
	}
</style>
