export const colors = {
	void: '#0d0d0d',
	iron: '#1a1510',
	rust: '#3a3020',
	bronze: '#5a4a30',
	parchment: '#d4c4a0',
	steel: '#8a8070',
	orange: '#ff9a00',
	ember: '#ff6a00',
	green: '#5cb85c',
	red: '#d9534f',
	concrete: '#6a6050',
	blue: '#4a90d9',
} as const;

export const tierColors = {
	bronze: '#CD7F32',
	silver: '#C0C0C0',
	gold: '#FFD700',
	platinum: '#E5E4E2',
} as const;

export const statusConfig = {
	keep: { color: colors.green, icon: '✓', label: 'KEEP' },
	discard: { color: colors.concrete, icon: '✗', label: 'DISCARD' },
	crash: { color: colors.red, icon: '💥', label: 'CRASH' },
} as const;

export type Status = keyof typeof statusConfig;
export type Tier = keyof typeof tierColors;
