<script lang="ts">
	import { onMount } from 'svelte';
	import FilterBar from './FilterBar.svelte';
	import Pagination from './Pagination.svelte';
	import TaskTable from './TaskTable.svelte';
	import TaskForm from './TaskForm.svelte';
	import ThemeToggle from './ThemeToggle.svelte';
	import type { Task } from '../types';
	import { Button } from '$lib/components/ui/button';

	// Use $state for reactive state
	let tasks = $state<Task[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Filters
	let searchQuery = $state('');
	let statusFilter = $state('');
	let priorityFilter = $state('');

	// Sorting
	let sortField = $state<keyof Task>('title');
	let sortDirection = $state<'asc' | 'desc'>('asc');

	// Pagination
	let currentPage = $state(1);
	let pageSize = $state(10);

	// Editing
	let editingTask = $state<Task | null>(null);

	// Show/Hide Add form
	let showAddForm = $state(false);

	// Configuration values
	let priorityValues = $state<string[]>([]);
	let statusValues = $state<string[]>([]);
	let colorValues = $state<string[]>([]);

	// --- Lifecycle ---
	onMount(async () => {
		await fetchConfig();
		await fetchTasks();
	});

	// --- Methods ---

	// Fetch configuration values from your API
	async function fetchConfig() {
		try {
			const response = await fetch('/config');
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			const config = await response.json();
			priorityValues = config.priority_values;
			statusValues = config.status_values;
			colorValues = config.color_values;
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			console.error('Error fetching config:', err);
		}
	}

	// Fetch all tasks from your API
	async function fetchTasks() {
		loading = true;
		try {
			const response = await fetch('/tasks');
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			tasks = await response.json();
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			console.error('Error fetching tasks:', err);
		} finally {
			loading = false;
		}
	}

	// Add a new task (triggered when TaskForm emits 'save')
	async function addTask(newTask: Task) {
		try {
			// Log the task data being sent to help with debugging
			//console.log('Sending task data:', JSON.stringify(newTask));

			// Ensure all required fields are present
			const taskToSend = {
				...newTask,
				status: newTask.status || statusValues[0] || 'Pending',
				priority: newTask.priority || priorityValues[0] || 'Medium',
				color: newTask.color || colorValues[0] || 'Blue',
				full_text: newTask.full_text || ''
			};

			const response = await fetch('/tasks', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(taskToSend)
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(`HTTP error! Status: ${response.status}, Details: ${errorText}`);
			}

			// Re-fetch or push to tasks array if server returns the new task
			await fetchTasks();
			showAddForm = false;
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			console.error('Error adding task:', err);
		}
	}

	// Delete a task
	async function deleteTask(id: number) {
		if (!confirm('Are you sure you want to delete this task?')) return;
		try {
			const response = await fetch(`/tasks/${id}`, { method: 'DELETE' });
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			tasks = tasks.filter((t) => t.id !== id);
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			console.error('Error deleting task:', err);
		}
	}

	// Bulk delete tasks
	async function bulkDeleteTasks(ids: number[]) {
		try {
			// Since we don't have a bulk delete endpoint, we'll delete tasks one by one
			let successCount = 0;
			let failCount = 0;

			for (const id of ids) {
				try {
					const response = await fetch(`/tasks/${id}`, { method: 'DELETE' });
					if (response.ok) {
						successCount++;
					} else {
						failCount++;
						console.error(`Failed to delete task ${id}: HTTP error ${response.status}`);
					}
				} catch (err) {
					failCount++;
					console.error(`Failed to delete task ${id}:`, err);
				}
			}

			// Update the local tasks array
			tasks = tasks.filter((t) => !ids.includes(t.id));

			// Show a summary message
			if (failCount > 0) {
				error = `Deleted ${successCount} tasks, but failed to delete ${failCount} tasks.`;
			}
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			console.error('Error in bulk delete:', err);
		}
	}

	// Start editing a task
	function startEdit(task: Task) {
		editingTask = { ...task };
	}

	// Cancel editing
	function cancelEdit() {
		editingTask = null;
	}

	// Save edited task
	async function saveEdit(updatedTask: Task) {
		try {
			const response = await fetch(`/tasks/${updatedTask.id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(updatedTask)
			});
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			// Update local tasks array
			tasks = tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t));
			editingTask = null;
		} catch (err: unknown) {
			error = err instanceof Error ? err.message : 'An unknown error occurred';
			console.error('Error updating task:', err);
		}
	}

	// Handle filter changes from FilterBar
	function handleFilterChange(
		e: CustomEvent<{ search: string; status: string; priority: string }>
	) {
		const { search, status, priority } = e.detail;
		searchQuery = search;
		statusFilter = status;
		priorityFilter = priority;
		// reset to page 1 if needed
		currentPage = 1;
	}

	// Handle sorting
	function setSort(field: keyof Task) {
		if (sortField === field) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortField = field;
			sortDirection = 'asc';
		}
	}

	// Pagination handlers
	function goToPage(page: number) {
		currentPage = page;
	}
	function goToPreviousPage() {
		if (currentPage > 1) currentPage--;
	}
	function goToNextPage() {
		currentPage++;
	}

	// Use $derived for computed values
	let filteredTasks = $derived(
		tasks.filter((t) => {
			const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase());
			const matchesStatus = statusFilter ? t.status === statusFilter : true;
			const matchesPriority = priorityFilter ? t.priority === priorityFilter : true;
			return matchesSearch && matchesStatus && matchesPriority;
		})
	);

	// Sort filtered tasks
	let sortedTasks = $derived(
		filteredTasks.slice().sort((a, b) => {
			const valA = (a[sortField] ?? '').toString().toLowerCase();
			const valB = (b[sortField] ?? '').toString().toLowerCase();
			if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
			if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
			return 0;
		})
	);

	// Calculate pagination
	let totalPages = $derived(Math.ceil(filteredTasks.length / pageSize) || 1);
	let displayedTasks = $derived(
		sortedTasks.slice((currentPage - 1) * pageSize, currentPage * pageSize)
	);
</script>

<main
	class="mx-auto min-h-screen max-w-6xl p-6 transition-colors duration-200 dark:bg-gray-900 dark:text-white"
>
	<!-- Header with Theme Toggle -->
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-slate-800 dark:text-white">Tasklist3000</h1>
			<p class="text-gray-600 dark:text-gray-400">Clean task management</p>
		</div>
		<ThemeToggle />
	</div>

	<!-- Error Alert -->
	{#if error}
		<div
			class="mb-4 flex items-center justify-between rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700 dark:border-red-700 dark:bg-red-900 dark:text-red-300"
		>
			<p>Error: {error}</p>
			<Button variant="ghost" size="sm" onclick={() => (error = null)}>Dismiss</Button>
		</div>
	{/if}

	<!-- Filter Bar -->
	<FilterBar {statusValues} {priorityValues} on:filterChange={handleFilterChange} />

	<!-- Add Task Button -->
	<div class="mb-4 flex justify-end">
		{#if !showAddForm}
			<Button variant="default" onclick={() => (showAddForm = true)}>Add New Task</Button>
		{/if}
	</div>

	<!-- Task Form for Adding -->
	{#if showAddForm}
		<TaskForm
			{priorityValues}
			{statusValues}
			{colorValues}
			on:cancel={() => (showAddForm = false)}
			on:save={(e) => addTask(e.detail)}
		/>
	{/if}

	<!-- Loading / No tasks states -->
	{#if loading}
		<div class="text-center italic text-gray-500 dark:text-gray-400">Loading tasks...</div>
	{:else if tasks.length === 0}
		<div class="py-10 text-center text-gray-500 dark:text-gray-400">
			No tasks found. Create your first task!
		</div>
	{:else}
		<!-- Table of tasks -->
		<TaskTable
			{displayedTasks}
			{sortField}
			{sortDirection}
			on:setSort={(e) => setSort(e.detail)}
			on:editTask={(e) => startEdit(e.detail)}
			on:deleteTask={(e) => deleteTask(e.detail)}
			on:bulkDelete={(e) => bulkDeleteTasks(e.detail)}
		/>

		<!-- Task Form for Editing -->
		{#if editingTask}
			<TaskForm
				task={editingTask}
				{priorityValues}
				{statusValues}
				{colorValues}
				on:cancel={cancelEdit}
				on:save={(e) => saveEdit(e.detail)}
			/>
		{/if}

		<!-- Pagination -->
		<Pagination
			{currentPage}
			{totalPages}
			{pageSize}
			on:setPage={(e) => goToPage(e.detail)}
			on:previous={goToPreviousPage}
			on:next={goToNextPage}
			on:setPageSize={(e) => {
				pageSize = e.detail;
				currentPage = 1;
			}}
		/>
	{/if}
</main>
