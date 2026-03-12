import { writable } from 'svelte/store';
import { experiments } from './experiments';
import { stats } from './stats';
import { achievements, newlyUnlocked } from './achievements';
import { techTree } from './techtree';
import { addActivity } from './activity';
import { updateTraining } from './training';

export const connectionStatus = writable<'connecting' | 'connected' | 'disconnected'>('disconnected');

let retryCount = 0;
let source: EventSource | null = null;

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
		if (data.tech_tree) techTree.set(data.tech_tree);

		// Build initial activity feed from results
		const items = (data.results || []).map((r: any, i: number) => ({
			type: 'experiment' as const,
			timestamp: new Date().toISOString(),
			data: { ...r, index: i },
		}));
		// Only keep last 50 for initial load
		const recent = items.slice(-50).reverse();
		recent.forEach((item: any) => addActivity(item));
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
		const ach = JSON.parse(e.data);
		achievements.update((list) =>
			list.map((a) => (a.id === ach.id ? { ...a, unlocked: true, unlocked_at: new Date().toISOString() } : a))
		);
		newlyUnlocked.set(ach);
		addActivity({
			type: 'achievement',
			timestamp: new Date().toISOString(),
			data: ach,
		});
		// Clear toast after 5s
		setTimeout(() => newlyUnlocked.set(null), 5000);
	});

	source.addEventListener('techtree_update', (e: MessageEvent) => {
		techTree.set(JSON.parse(e.data));
	});

	source.addEventListener('training_progress', (e: MessageEvent) => {
		updateTraining(JSON.parse(e.data));
	});
}
