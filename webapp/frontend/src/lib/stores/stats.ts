import { writable } from 'svelte/store';

export interface Stats {
	total_runs: number;
	total_keeps: number;
	total_discards: number;
	total_crashes: number;
	best_bpb: number | null;
	baseline_bpb: number | null;
	success_rate: number;
	consecutive_keeps: number;
	max_consecutive_keeps: number;
	improvements: number[];
}

export const stats = writable<Stats>({
	total_runs: 0,
	total_keeps: 0,
	total_discards: 0,
	total_crashes: 0,
	best_bpb: null,
	baseline_bpb: null,
	success_rate: 0,
	consecutive_keeps: 0,
	max_consecutive_keeps: 0,
	improvements: [],
});
