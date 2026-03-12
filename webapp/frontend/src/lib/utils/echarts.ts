import { colors } from '$lib/theme/factorio';
import type { Experiment } from '$lib/stores/experiments';

export function buildBpbChartOption(experiments: Experiment[]) {
	const keepData: [number, number][] = [];
	const discardData: [number, number][] = [];
	const crashData: [number, number][] = [];
	const frontierData: [number, number][] = [];
	const descriptions: Map<number, Experiment> = new Map();

	let runningMin = Infinity;

	experiments.forEach((e, i) => {
		descriptions.set(i, e);
		if (e.status === 'keep' && e.val_bpb > 0) {
			keepData.push([i, e.val_bpb]);
			if (e.val_bpb < runningMin) {
				runningMin = e.val_bpb;
			}
			frontierData.push([i, runningMin]);
		} else if (e.status === 'crash' || e.val_bpb === 0) {
			crashData.push([i, 0]);
		} else {
			if (e.val_bpb > 0) discardData.push([i, e.val_bpb]);
		}
	});

	const baseline = experiments.length > 0 ? experiments[0].val_bpb : null;

	return {
		backgroundColor: 'transparent',
		animation: true,
		animationDuration: 300,
		grid: {
			top: 40,
			right: 20,
			bottom: 60,
			left: 70,
		},
		tooltip: {
			trigger: 'item' as const,
			backgroundColor: colors.iron,
			borderColor: colors.rust,
			textStyle: { color: colors.parchment, fontFamily: '"JetBrains Mono", monospace', fontSize: 11 },
			formatter: (params: any) => {
				const idx = params.data[0];
				const exp = descriptions.get(idx);
				if (!exp) return '';
				return [
					`<strong>Experiment #${idx}</strong>`,
					`BPB: ${exp.val_bpb > 0 ? exp.val_bpb.toFixed(6) : 'CRASH'}`,
					`Status: ${exp.status.toUpperCase()}`,
					`"${exp.description}"`,
					`Commit: ${exp.commit}`,
				].join('<br/>');
			},
		},
		xAxis: {
			type: 'value' as const,
			name: 'Experiment #',
			nameTextStyle: { color: colors.steel, fontSize: 10 },
			axisLine: { lineStyle: { color: colors.rust } },
			splitLine: { lineStyle: { color: colors.iron } },
			axisLabel: { color: colors.steel, fontSize: 10 },
		},
		yAxis: {
			type: 'value' as const,
			name: 'val_bpb',
			nameTextStyle: { color: colors.steel, fontSize: 10 },
			axisLine: { lineStyle: { color: colors.rust } },
			splitLine: { lineStyle: { color: colors.iron } },
			axisLabel: { color: colors.steel, fontSize: 10, formatter: (v: number) => v.toFixed(3) },
		},
		dataZoom: [
			{
				type: 'slider' as const,
				height: 20,
				bottom: 8,
				borderColor: colors.rust,
				backgroundColor: colors.void,
				fillerColor: 'rgba(255, 154, 0, 0.1)',
				handleStyle: { color: colors.orange },
				textStyle: { color: colors.steel },
				dataBackground: {
					lineStyle: { color: colors.rust },
					areaStyle: { color: 'rgba(255, 154, 0, 0.05)' },
				},
			},
		],
		series: [
			{
				name: 'Keep',
				type: 'scatter',
				data: keepData,
				symbolSize: 8,
				itemStyle: {
					color: colors.green,
					borderColor: colors.void,
					borderWidth: 1,
				},
				z: 3,
			},
			{
				name: 'Discard',
				type: 'scatter',
				data: discardData,
				symbolSize: 4,
				itemStyle: {
					color: colors.concrete,
					opacity: 0.5,
				},
				z: 1,
			},
			{
				name: 'Crash',
				type: 'scatter',
				data: crashData,
				symbol: 'diamond',
				symbolSize: 6,
				itemStyle: {
					color: colors.red,
				},
				z: 2,
			},
			{
				name: 'Frontier',
				type: 'line',
				data: frontierData,
				step: 'end',
				lineStyle: {
					color: colors.orange,
					width: 2,
				},
				itemStyle: { color: colors.orange },
				showSymbol: false,
				z: 4,
			},
			...(baseline
				? [
						{
							name: 'Baseline',
							type: 'line' as const,
							markLine: {
								silent: true,
								symbol: 'none',
								lineStyle: { color: colors.rust, type: 'dashed' as const, width: 1 },
								data: [{ yAxis: baseline, label: { formatter: 'BASELINE', color: colors.steel, fontSize: 9 } }],
							},
							data: [],
						},
					]
				: []),
		],
	};
}
