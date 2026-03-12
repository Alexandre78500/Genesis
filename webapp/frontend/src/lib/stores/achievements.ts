import { writable } from 'svelte/store';

export interface Achievement {
	id: string;
	name: string;
	description: string;
	tier: 'bronze' | 'silver' | 'gold' | 'platinum';
	icon: string;
	unlocked: boolean;
	unlocked_at: string | null;
}

export const achievements = writable<Achievement[]>([]);
export const newlyUnlocked = writable<Achievement | null>(null);
