import { get, writable } from 'svelte/store';
import type { ActivityItem } from './activity';
import { addActivity, setActivityFeed } from './activity';
import { achievements, newlyUnlocked } from './achievements';
import { experiments } from './experiments';
import { stats } from './stats';
import {
	appendTrainingSample,
	hydrateTraining,
	liveRun,
	setLiveRunState,
	type LiveRunState,
	type TrainingSample,
} from './training';
import { techTree } from './techtree';

export const connectionStatus = writable<'connecting' | 'connected' | 'disconnected'>('disconnected');

let retryCount = 0;
let source: EventSource | null = null;

function buildExperimentActivities(results: any[]): ActivityItem[] {
	const baseTime = Date.now();
	return results
		.map((result: any, index: number) => ({
			type: 'experiment' as const,
			timestamp: new Date(baseTime - (results.length - index) * 1000).toISOString(),
			data: { ...result, index },
		}))
		.slice(-50)
		.reverse();
}

function buildLiveActivity(run: Partial<LiveRunState> | null | undefined): ActivityItem | null {
	if (!run || !run.status || run.status === 'idle') {
		return null;
	}

	const result = run.last_result;
	const resultSummary =
		result && typeof result === 'object'
			? ` · ${result.status.toUpperCase()} ${result.commit?.slice(0, 7) || ''} ${result.val_bpb?.toFixed?.(4) || ''}`.trim()
			: '';

	return {
		type: 'system',
		timestamp: run.last_seen_at || run.started_at || new Date().toISOString(),
		data: `${run.status.toUpperCase()} — ${run.status_message || 'live run update'}${resultSummary ? ` ${resultSummary}` : ''}`,
	};
}

function hydrateActivityFeed(data: any) {
	const items = buildExperimentActivities(data.results || []);
	const liveItem = buildLiveActivity(data.live_run);
	setActivityFeed(liveItem ? [liveItem, ...items].slice(0, 50) : items);
}

export function initSSE() {
	if (source) {
		source.close();
	}

	connectionStatus.set('connecting');
	source = new EventSource('/api/stream');

	source.onopen = () => {
		connectionStatus.set('connected');
		retryCount = 0;
	};

	source.onerror = () => {
		source?.close();
		source = null;
		connectionStatus.set('disconnected');
		const delay = Math.min(1000 * 2 ** retryCount, 30000);
		retryCount++;
		setTimeout(initSSE, delay);
	};

	source.addEventListener('snapshot', (e: MessageEvent) => {
		const data = JSON.parse(e.data);
		experiments.set(data.results || []);
		stats.set(data.stats || {});
		achievements.set(data.achievements || []);
		if (data.tech_tree) {
			techTree.set(data.tech_tree);
		}
		hydrateTraining({
			live_run: data.live_run,
			recent_steps: data.recent_steps,
		});
		hydrateActivityFeed(data);
	});

	source.addEventListener('new_result', (e: MessageEvent) => {
		const result = JSON.parse(e.data);
		experiments.update((list) => [...list, result]);
		addActivity({
			type: 'experiment',
			timestamp: new Date().toISOString(),
			data: result,
		});
	});

	source.addEventListener('stats_update', (e: MessageEvent) => {
		stats.set(JSON.parse(e.data));
	});

	source.addEventListener('achievement_unlocked', (e: MessageEvent) => {
		const achievement = JSON.parse(e.data);
		achievements.update((list) =>
			list.map((item) =>
				item.id === achievement.id
					? { ...item, unlocked: true, unlocked_at: new Date().toISOString() }
					: item
			)
		);
		newlyUnlocked.set(achievement);
		addActivity({
			type: 'achievement',
			timestamp: new Date().toISOString(),
			data: achievement,
		});
		setTimeout(() => newlyUnlocked.set(null), 5000);
	});

	source.addEventListener('techtree_update', (e: MessageEvent) => {
		techTree.set(JSON.parse(e.data));
	});

	source.addEventListener('live_state', (e: MessageEvent) => {
		const nextState = JSON.parse(e.data) as LiveRunState;
		const previousState = get(liveRun);
		setLiveRunState(nextState);

		if (
			nextState.status !== 'idle' &&
			(previousState.run_id !== nextState.run_id || previousState.status !== nextState.status)
		) {
			const activity = buildLiveActivity(nextState);
			if (activity) {
				addActivity(activity);
			}
		}
	});

	source.addEventListener('training_step', (e: MessageEvent) => {
		appendTrainingSample(JSON.parse(e.data) as TrainingSample);
	});
}
