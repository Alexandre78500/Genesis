export function formatBpb(val: number | null): string {
	if (val === null || val === 0) return '---';
	return val.toFixed(6);
}

export function formatPct(val: number): string {
	const sign = val >= 0 ? '+' : '';
	return `${sign}${val.toFixed(3)}%`;
}

export function formatRelativeTime(iso: string): string {
	const now = Date.now();
	const then = new Date(iso).getTime();
	const diff = Math.floor((now - then) / 1000);

	if (diff < 60) return `${diff}s ago`;
	if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
	if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
	return `${Math.floor(diff / 86400)}d ago`;
}

export function formatMemory(gb: number): string {
	if (gb === 0) return '---';
	return `${gb.toFixed(1)} GB`;
}

export function formatNumber(n: number): string {
	return n.toLocaleString();
}
