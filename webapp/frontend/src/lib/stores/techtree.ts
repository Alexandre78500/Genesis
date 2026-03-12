import { writable } from 'svelte/store';

export interface TechNode {
	id: string;
	label: string;
	type: 'tier' | 'concept';
	tier: string;
	status: 'locked' | 'unlocked' | 'explored' | 'mastered';
	experiments: number;
	keeps: number;
	best_bpb?: number | null;
	size: number;
}

export interface TechEdge {
	source: string;
	target: string;
	type?: string;
}

export interface TechTreeData {
	nodes: TechNode[];
	edges: TechEdge[];
}

export const techTree = writable<TechTreeData>({ nodes: [], edges: [] });
