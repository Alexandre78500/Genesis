import { writable } from 'svelte/store';
import type { Experiment } from './experiments';
import type { Achievement } from './achievements';

export interface ActivityItem {
	type: 'experiment' | 'achievement' | 'system';
	timestamp: string;
	data: Experiment | Achievement | string;
}

export const activityFeed = writable<ActivityItem[]>([]);

const MAX_ITEMS = 200;

export function addActivity(item: ActivityItem) {
	activityFeed.update((feed) => {
		const updated = [item, ...feed];
		return updated.slice(0, MAX_ITEMS);
	});
}

export function setActivityFeed(items: ActivityItem[]) {
	activityFeed.set(items.slice(0, MAX_ITEMS));
}
