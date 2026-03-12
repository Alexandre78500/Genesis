import { writable } from 'svelte/store';

export interface TrainingProgress {
	step: number;
	progress_pct: number;
	loss: number;
	lr_mult: number;
	dt_ms: number;
	tok_per_sec: string;
	mfu: number;
	epoch: number;
	remaining_s: number;
}

export const trainingProgress = writable<TrainingProgress | null>(null);
export const isTraining = writable(false);

let trainingTimeout: ReturnType<typeof setTimeout> | null = null;

export function updateTraining(data: TrainingProgress) {
	trainingProgress.set(data);
	isTraining.set(true);

	// If no update for 60s, mark as idle (M4 steps can take 20-30s each)
	if (trainingTimeout) clearTimeout(trainingTimeout);
	trainingTimeout = setTimeout(() => {
		isTraining.set(false);
	}, 60000);
}
