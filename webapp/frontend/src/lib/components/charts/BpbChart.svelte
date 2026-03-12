<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { experiments } from '$lib/stores/experiments';
	import { buildBpbChartOption } from '$lib/utils/echarts';
	import * as echarts from 'echarts';

	let chartContainer: HTMLDivElement;
	let chart: echarts.ECharts | null = null;

	onMount(() => {
		chart = echarts.init(chartContainer, undefined, { renderer: 'canvas' });
		const option = buildBpbChartOption($experiments);
		chart.setOption(option);

		const observer = new ResizeObserver(() => chart?.resize());
		observer.observe(chartContainer);

		return () => {
			observer.disconnect();
			chart?.dispose();
		};
	});

	$effect(() => {
		if (chart && $experiments) {
			const option = buildBpbChartOption($experiments);
			chart.setOption(option, { notMerge: false });
		}
	});
</script>

<div class="chart-wrapper" bind:this={chartContainer}></div>

<style>
	.chart-wrapper {
		width: 100%;
		height: 100%;
		min-height: 200px;
	}
</style>
