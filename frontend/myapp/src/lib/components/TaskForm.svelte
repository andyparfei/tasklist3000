<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import type { Task } from '../types';
	import * as Select from '$lib/components/ui/select/index.js';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';

	// Props using $props() for Svelte 5 runes mode
	const props = $props<{
		task?: Task | null;
		priorityValues?: string[];
		statusValues?: string[];
		colorValues?: string[];
	}>();

	// Initialize props with default values
	let task = $derived(props.task || null);
	let priorityValues = $derived(props.priorityValues || []);
	let statusValues = $derived(props.statusValues || []);
	let colorValues = $derived(props.colorValues || []);

	const dispatch = createEventDispatcher();

	// Function to get CSS color value from color name
	function getColorValue(colorName: string): string {
		const colorMap: Record<string, string> = {
			Red: '#ef4444',
			Green: '#22c55e',
			Blue: '#3b82f6',
			Yellow: '#eab308',
			Purple: '#a855f7',
			// Default color if none matches
			default: '#cbd5e1'
		};

		return colorMap[colorName] || colorMap.default;
	}

	// localTask holds the form's working copy.
	// When adding, it starts as a new task.
	// When editing, it starts as a clone of the passed-in task.
	let localTask = $state<Task>({
		id: 0,
		title: '',
		description: '',
		status: '',
		priority: '',
		color: '',
		full_text: ''
	});

	// Initialize localTask based on whether we're editing or adding.
	function initializeLocalTask() {
		if (task) {
			localTask = { ...task };
		} else {
			localTask = {
				id: 0,
				title: '',
				description: '',
				status: statusValues[0] || 'Pending',
				priority: priorityValues[0] || 'Medium',
				color: colorValues[0] || 'Blue',
				full_text: ''
			};
		}
	}

	onMount(() => {
		initializeLocalTask();
	});

	// Watch for changes to task
	$effect(() => {
		if (task && task.id !== localTask.id) {
			initializeLocalTask();
		}
	});

	function save() {
		// Prevent saving if the title is empty.
		if (!localTask.title.trim()) return;

		// Ensure all required fields are set
		const taskToSave = {
			...localTask,
			// Ensure these fields are never empty
			status: localTask.status || statusValues[0] || 'Pending',
			priority: localTask.priority || priorityValues[0] || 'Medium',
			color: localTask.color || colorValues[0] || 'Blue',
			full_text: localTask.full_text || ''
		};

		// Emit the save event with the current task data.
		dispatch('save', taskToSave);

		// When adding a new task (i.e. task is null), reset the form for a subsequent add.
		if (!task) {
			initializeLocalTask();
		}
	}

	function cancel() {
		dispatch('cancel');
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		save();
	}
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
	<div class="w-full max-w-md rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
		<h2 class="mb-4 text-xl font-bold dark:text-white">{task ? 'Edit Task' : 'Add Task'}</h2>
		<p class="mb-4 text-gray-600 dark:text-gray-400">
			{task ? 'Make changes to your task below.' : 'Enter details for your new task.'}
		</p>

		<!-- Using form submission for saving to avoid duplicate events -->
		<form onsubmit={handleSubmit} class="space-y-4">
			<div>
				<Label for="title" class="text-gray-700 dark:text-gray-300">Title</Label>
				<Input
					id="title"
					type="text"
					bind:value={localTask.title}
					required
					class="mt-1 dark:bg-gray-700 dark:text-white"
				/>
			</div>

			<div>
				<Label for="status" class="text-gray-700 dark:text-gray-300">Status</Label>
				<Select.Root type="single" bind:value={localTask.status} required>
					<Select.Trigger class="mt-1 w-full">
						{localTask.status || 'Select a status'}
					</Select.Trigger>
					<Select.Content>
						{#each statusValues as status}
							<Select.Item value={status}>{status}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			<div>
				<Label for="priority" class="text-gray-700 dark:text-gray-300">Priority</Label>
				<Select.Root type="single" bind:value={localTask.priority} required>
					<Select.Trigger class="mt-1 w-full">
						{localTask.priority || 'Select a priority'}
					</Select.Trigger>
					<Select.Content>
						{#each priorityValues as priority}
							<Select.Item value={priority}>{priority}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			<div>
				<Label class="mb-2 text-gray-700 dark:text-gray-300">Color</Label>
				<div class="flex flex-wrap gap-2">
					{#each colorValues as color}
						<button
							type="button"
							class="flex h-10 w-10 items-center justify-center rounded-full border-2 transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
							style="background-color: {getColorValue(color)}; border-color: {localTask.color ===
							color
								? '#000'
								: 'transparent'};"
							onclick={() => (localTask.color = color)}
							title={color}
						>
							{#if localTask.color === color}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="h-6 w-6 text-white"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M5 13l4 4L19 7"
									/>
								</svg>
							{/if}
						</button>
					{/each}
				</div>
				<div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
					Selected: <span class="font-medium dark:text-gray-300">{localTask.color}</span>
				</div>
			</div>

			<div>
				<Label for="description" class="text-gray-700 dark:text-gray-300">Description</Label>
				<Textarea
					id="description"
					bind:value={localTask.description}
					rows="3"
					class="mt-1 dark:bg-gray-700 dark:text-white"
					required
				/>
			</div>

			<div>
				<Label for="full_text" class="text-gray-700 dark:text-gray-300">Full Text</Label>
				<Textarea
					id="full_text"
					bind:value={localTask.full_text}
					rows="3"
					class="mt-1 dark:bg-gray-700 dark:text-white"
				/>
			</div>

			<div class="flex justify-end space-x-2 pt-4">
				<Button type="button" variant="secondary" onclick={cancel}>Cancel</Button>
				<Button type="submit" variant="default">Save</Button>
			</div>
		</form>
	</div>
</div>
