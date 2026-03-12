<script lang="ts">
	import { onMount } from 'svelte';
	import { techTree } from '$lib/stores/techtree';
	import { colors } from '$lib/theme/factorio';
	import * as echarts from 'echarts';

	let chartContainer: HTMLDivElement;
	let chart: echarts.ECharts | null = null;

	const tierColors: Record<string, string> = {
		tier1_foundations: '#CD7F32',
		tier2_architecture: '#C0C0C0',
		tier3_optimization: '#FFD700',
		tier4_innovation: '#E5E4E2',
	};

	const statusOpacity: Record<string, number> = {
		locked: 0.2,
		unlocked: 0.4,
		explored: 0.6,
		mastered: 1.0,
	};

	function buildTreeOption(data: typeof $techTree) {
		if (!data?.nodes?.length) {
			return {
				backgroundColor: 'transparent',
				graphic: {
					type: 'text',
					left: 'center',
					top: 'center',
					style: {
						text: 'NO RESEARCH DATA',
						fill: colors.steel,
						font: '11px "JetBrains Mono", monospace',
					},
				},
				series: [],
			};
		}

		const nodes = data.nodes.map((n) => ({
			id: n.id,
			name: n.label,
			symbolSize: n.size,
			value: n.experiments,
			category: n.tier,
			itemStyle: {
				color: tierColors[n.tier] || colors.steel,
				opacity: statusOpacity[n.status] || 0.5,
				borderColor: n.status === 'mastered' ? tierColors[n.tier] : colors.rust,
				borderWidth: n.type === 'tier' ? 3 : 1,
			},
			label: {
				show: n.type === 'tier' || n.experiments > 0,
				color: colors.parchment,
				fontSize: n.type === 'tier' ? 11 : 9,
			},
		}));

		const links = data.edges.map((e) => ({
			source: e.source,
			target: e.target,
			lineStyle: {
				color: e.type === 'cross' ? colors.rust : colors.bronze,
				opacity: 0.4,
				curveness: e.type === 'cross' ? 0.3 : 0.1,
			},
		}));

		return {
			backgroundColor: 'transparent',
			tooltip: {
				backgroundColor: colors.iron,
				borderColor: colors.rust,
				textStyle: { color: colors.parchment, fontFamily: '"JetBrains Mono", monospace', fontSize: 10 },
				formatter: (params: any) => {
					const node = data.nodes.find((n) => n.id === params.data?.id);
					if (!node) return '';
					return [
						`<strong>${node.label}</strong>`,
						`Status: ${node.status.toUpperCase()}`,
						`Experiments: ${node.experiments}`,
						`Keeps: ${node.keeps}`,
						node.best_bpb ? `Best BPB: ${node.best_bpb.toFixed(6)}` : '',
					]
						.filter(Boolean)
						.join('<br/>');
				},
			},
			series: [
				{
					type: 'graph',
					layout: 'force',
					data: nodes,
					links: links,
					roam: true,
					force: {
						repulsion: 120,
						edgeLength: [40, 100],
						gravity: 0.1,
					},
					lineStyle: { width: 1 },
					emphasis: {
						focus: 'adjacency',
						lineStyle: { width: 2 },
					},
				},
			],
		};
	}

	onMount(() => {
		chart = echarts.init(chartContainer, undefined, { renderer: 'canvas' });
		chart.setOption(buildTreeOption($techTree));

		const observer = new ResizeObserver(() => chart?.resize());
		observer.observe(chartContainer);

		return () => {
			observer.disconnect();
			chart?.dispose();
		};
	});

	$effect(() => {
		if (chart && $techTree) {
			chart.setOption(buildTreeOption($techTree), { notMerge: true });
		}
	});
</script>

<div class="tree-wrapper" bind:this={chartContainer}></div>

<style>
	.tree-wrapper {
		width: 100%;
		height: 100%;
		min-height: 150px;
	}
</style>
