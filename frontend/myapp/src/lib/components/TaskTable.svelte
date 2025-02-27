<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Task } from '../types';
	import { Checkbox } from '$lib/components/ui/checkbox/index.js';
	import {
		DropdownMenu,
		DropdownMenuContent,
		DropdownMenuItem,
		DropdownMenuTrigger
	} from '$lib/components/ui/dropdown-menu';
	import { Button } from '$lib/components/ui/button';

	// Props using $props() for Svelte 5 runes mode
	const props = $props<{
		displayedTasks: Task[];
		sortField: keyof Task;
		sortDirection: 'asc' | 'desc';
	}>();

	// Track selected tasks
	let selectedTasks = $state(new Set<number>());
	let selectAll = $state(false);

	const dispatch = createEventDispatcher();

	function toggleSort(field: keyof Task) {
		dispatch('setSort', field);
	}

	function editTask(task: Task) {
		dispatch('editTask', task);
	}

	function deleteTask(id: number) {
		dispatch('deleteTask', id);
	}

	function toggleSelectAll() {
		if (selectAll) {
			// Deselect all
			selectedTasks = new Set();
		} else {
			// Select all
			selectedTasks = new Set(props.displayedTasks.map((task) => task.id));
		}
		selectAll = !selectAll;
	}

	function toggleSelectTask(id: number) {
		const newSelectedTasks = new Set(selectedTasks);

		if (newSelectedTasks.has(id)) {
			newSelectedTasks.delete(id);
			selectAll = false;
		} else {
			newSelectedTasks.add(id);
			// Check if all tasks are now selected
			if (newSelectedTasks.size === props.displayedTasks.length) {
				selectAll = true;
			}
		}

		selectedTasks = newSelectedTasks;
	}

	function bulkDeleteTasks() {
		if (selectedTasks.size === 0) return;

		if (confirm(`Are you sure you want to delete ${selectedTasks.size} task(s)?`)) {
			dispatch('bulkDelete', Array.from(selectedTasks));
			selectedTasks = new Set();
			selectAll = false;
		}
	}

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
</script>

<div class="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
	{#if selectedTasks.size > 0}
		<div
			class="flex items-center justify-between border-b border-gray-200 bg-gray-50 p-2 dark:border-gray-700 dark:bg-gray-800"
		>
			<div>
				<span class="text-sm font-medium dark:text-gray-300"
					>{selectedTasks.size} task{selectedTasks.size > 1 ? 's' : ''} selected</span
				>
			</div>
			<Button variant="destructive" size="sm" onclick={bulkDeleteTasks}>Delete Selected</Button>
		</div>
	{/if}
	<table class="min-w-full bg-white text-left dark:bg-gray-800">
		<thead class="border-b border-gray-200 bg-gray-50 dark:border-gray-600 dark:bg-gray-700">
			<tr>
				<th class="w-10 px-4 py-2">
					<Checkbox checked={selectAll} onclick={toggleSelectAll} />
				</th>
				<th class="w-16 cursor-pointer px-4 py-2" onclick={() => toggleSort('color')}>
					Color
					{#if props.sortField === 'color'}
						{props.sortDirection === 'asc' ? ' ▲' : ' ▼'}
					{/if}
				</th>
				<th class="cursor-pointer px-4 py-2" onclick={() => toggleSort('title')}>
					Title
					{#if props.sortField === 'title'}
						{props.sortDirection === 'asc' ? ' ▲' : ' ▼'}
					{/if}
				</th>
				<th class="cursor-pointer px-4 py-2" onclick={() => toggleSort('status')}>
					Status
					{#if props.sortField === 'status'}
						{props.sortDirection === 'asc' ? ' ▲' : ' ▼'}
					{/if}
				</th>
				<th class="cursor-pointer px-4 py-2" onclick={() => toggleSort('priority')}>
					Priority
					{#if props.sortField === 'priority'}
						{props.sortDirection === 'asc' ? ' ▲' : ' ▼'}
					{/if}
				</th>
				<th class="px-4 py-2">Description</th>
				<th class="px-4 py-2 text-right">Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each props.displayedTasks as task}
				<tr
					class="relative border-b border-gray-100 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700"
					style="border-left: 4px solid {getColorValue(
						task.color
					)}; box-shadow: inset 0 0 0 9999px rgba({task.color === 'Yellow'
						? '234, 179, 8, 0.03'
						: task.color === 'Red'
							? '239, 68, 68, 0.03'
							: task.color === 'Green'
								? '34, 197, 94, 0.03'
								: task.color === 'Blue'
									? '59, 130, 246, 0.03'
									: task.color === 'Purple'
										? '168, 85, 247, 0.03'
										: '0, 0, 0, 0'});"
				>
					<td class="w-10 px-4 py-2">
						<Checkbox
							checked={selectedTasks.has(task.id)}
							onclick={() => toggleSelectTask(task.id)}
						/>
					</td>
					<td class="w-16 px-4 py-2">
						<div class="flex items-center justify-center">
							<div
								class="h-6 w-6 rounded-full"
								style="background-color: {getColorValue(task.color)};"
								title={task.color}
							></div>
						</div>
					</td>
					<td class="px-4 py-2 dark:text-white">{task.title}</td>
					<td class="px-4 py-2">
						<span
							class="inline-flex items-center rounded-full border border-gray-300 px-2.5 py-0.5 text-xs font-semibold dark:border-gray-600 dark:text-gray-300"
						>
							{task.status}
						</span>
					</td>
					<td class="px-4 py-2">
						<span
							class="inline-flex items-center rounded-full border border-gray-300 px-2.5 py-0.5 text-xs font-semibold dark:border-gray-600 dark:text-gray-300"
						>
							{task.priority}
						</span>
					</td>
					<td class="px-4 py-2 dark:text-gray-300">{task.description}</td>
					<td class="px-4 py-2 text-right">
						<Button variant="outline" size="sm" onclick={() => editTask(task)}>Edit</Button>
						<DropdownMenu>
							<DropdownMenuTrigger
								class="ml-2 rounded bg-gray-200 px-3 py-1 transition-colors hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
							>
								...
							</DropdownMenuTrigger>
							<DropdownMenuContent>
								<DropdownMenuItem
									onclick={() => deleteTask(task.id)}
									class="text-red-500 dark:text-red-400"
								>
									Delete
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
