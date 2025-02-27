<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import * as Select from '$lib/components/ui/select';
	import { Input } from '$lib/components/ui/input';

	// Props using Svelte 5 runes
	const { statusValues = [], priorityValues = [] } = $props();

	// Use $state for reactive state
	let search = $state('');
	let status = $state('');
	let priority = $state('');

	const dispatch = createEventDispatcher();

	// Create a derived value that automatically updates
	let filters = $derived({
		search,
		status,
		priority
	});

	// Watch for changes to the derived value
	$effect(() => {
		console.log('Filters changed:', filters);
		dispatch('filterChange', filters);
	});

	// Derived options with "All" option at the beginning
	let statusOptions = $derived([
		{ value: '', label: 'All Statuses' },
		...statusValues.map((value) => ({ value, label: value }))
	]);

	let priorityOptions = $derived([
		{ value: '', label: 'All Priorities' },
		...priorityValues.map((value) => ({ value, label: value }))
	]);

	// Derived content for select triggers
	let statusTriggerContent = $derived(
		statusOptions.find((opt) => opt.value === status)?.label ?? 'All Statuses'
	);

	let priorityTriggerContent = $derived(
		priorityOptions.find((opt) => opt.value === priority)?.label ?? 'All Priorities'
	);
</script>

<div class="mb-4 flex flex-col items-center gap-2 md:flex-row">
	<Input placeholder="Search..." bind:value={search} class="w-full md:w-auto" />

	<div class="w-full md:w-auto">
		<Select.Root type="single" name="status" bind:value={status}>
			<Select.Trigger class="w-full md:w-[180px]">
				{statusTriggerContent}
			</Select.Trigger>
			<Select.Content>
				{#each statusOptions as option}
					<Select.Item value={option.value} label={option.label}>
						{option.label}
					</Select.Item>
				{/each}
			</Select.Content>
		</Select.Root>
	</div>

	<div class="w-full md:w-auto">
		<Select.Root type="single" name="priority" bind:value={priority}>
			<Select.Trigger class="w-full md:w-[180px]">
				{priorityTriggerContent}
			</Select.Trigger>
			<Select.Content>
				{#each priorityOptions as option}
					<Select.Item value={option.value} label={option.label}>
						{option.label}
					</Select.Item>
				{/each}
			</Select.Content>
		</Select.Root>
	</div>
	<!--<SuperDebug data={$priority} />-->
</div>
