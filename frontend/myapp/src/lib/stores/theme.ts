import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

// Initialize theme from localStorage or system preference
const getInitialTheme = (): Theme => {
	if (browser) {
		// Check localStorage first
		const storedTheme = localStorage.getItem('theme') as Theme | null;
		if (storedTheme) {
			return storedTheme;
		}

		// Check system preference
		if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
			return 'dark';
		}
	}

	// Default to light
	return 'light';
};

// Create the theme store
export const theme = writable<Theme>(getInitialTheme());

// Update localStorage and document class when theme changes
if (browser) {
	theme.subscribe((value) => {
		localStorage.setItem('theme', value);

		// Update document class for CSS
		if (value === 'dark') {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	});
}

// Toggle theme function
export function toggleTheme() {
	theme.update((current) => (current === 'light' ? 'dark' : 'light'));
}
