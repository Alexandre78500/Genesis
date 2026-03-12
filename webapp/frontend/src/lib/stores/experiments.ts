import { writable, derived } from 'svelte/store';

export interface Experiment {
	index?: number;
	commit: string;
	val_bpb: number;
	memory_gb: number;
	status: 'keep' | 'discard' | 'crash';
	description: string;
	is_new_best?: boolean;
}

export const experiments = writable<Experiment[]>([]);

export const latestExperiment = derived(experiments, ($e) => ($e.length > 0 ? $e[$e.length - 1] : null));

export const bestBpb = derived(experiments, ($e) => {
	const valid = $e.filter((e) => e.val_bpb > 0);
	return valid.length > 0 ? Math.min(...valid.map((e) => e.val_bpb)) : null;
});
