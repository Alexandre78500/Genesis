import { derived, writable } from 'svelte/store';
import type { Experiment } from './experiments';

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

export interface TrainingSample extends TrainingProgress {
	observed_at: string;
}

export type LiveRunStatus =
	| 'idle'
	| 'starting'
	| 'running'
	| 'stalled'
	| 'finishing'
	| 'completed'
	| 'crashed';

export interface LiveRunState {
	status: LiveRunStatus;
	run_id: string | null;
	started_at: string | null;
	last_seen_at: string | null;
	last_log_mtime: number | null;
	last_step_at: string | null;
	current_step: TrainingProgress | null;
	recent_steps: TrainingSample[];
	last_result: Experiment | null;
	status_message: string;
}

const defaultLiveRun = (): LiveRunState => ({
	status: 'idle',
	run_id: null,
	started_at: null,
	last_seen_at: null,
	last_log_mtime: null,
	last_step_at: null,
	current_step: null,
	recent_steps: [],
	last_result: null,
	status_message: 'awaiting next experiment',
});

function normalizeLiveRun(data: Partial<LiveRunState> | null | undefined): LiveRunState {
	return {
		...defaultLiveRun(),
		...(data || {}),
		recent_steps: (data?.recent_steps || []).slice(-100),
		current_step: data?.current_step || null,
		last_result: data?.last_result || null,
		status_message: data?.status_message || defaultLiveRun().status_message,
	};
}

export const liveRun = writable<LiveRunState>(defaultLiveRun());
export const trainingSamples = writable<TrainingSample[]>([]);

export const trainingProgress = derived(liveRun, ($liveRun) => $liveRun.current_step);
export const isTraining = derived(
	liveRun,
	($liveRun) => ['starting', 'running', 'stalled', 'finishing'].includes($liveRun.status)
);

export function hydrateTraining(data: {
	live_run?: Partial<LiveRunState> | null;
	recent_steps?: TrainingSample[];
}) {
	const nextLiveRun = normalizeLiveRun(data.live_run);
	const samples = (data.recent_steps || nextLiveRun.recent_steps || []).slice(-100);
	liveRun.set({ ...nextLiveRun, recent_steps: samples });
	trainingSamples.set(samples);
}

export function setLiveRunState(data: Partial<LiveRunState> | null | undefined) {
	const nextLiveRun = normalizeLiveRun(data);
	liveRun.update((current) => {
		const hasRecentSteps = Boolean(data && 'recent_steps' in data);
		const samples = hasRecentSteps ? nextLiveRun.recent_steps : current.recent_steps;
		trainingSamples.set(samples.slice(-100));
		return { ...current, ...nextLiveRun, recent_steps: samples.slice(-100) };
	});
}

export function appendTrainingSample(sample: TrainingSample) {
	trainingSamples.update((samples) => {
		const nextSamples = [...samples, sample].slice(-100);
		liveRun.update((current) => ({
			...current,
			current_step: {
				step: sample.step,
				progress_pct: sample.progress_pct,
				loss: sample.loss,
				lr_mult: sample.lr_mult,
				dt_ms: sample.dt_ms,
				tok_per_sec: sample.tok_per_sec,
				mfu: sample.mfu,
				epoch: sample.epoch,
				remaining_s: sample.remaining_s,
			},
			last_step_at: sample.observed_at,
			recent_steps: nextSamples,
		}));
		return nextSamples;
	});
}

export function resetTraining() {
	liveRun.set(defaultLiveRun());
	trainingSamples.set([]);
}
