<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import * as Select from '$lib/components/ui/select/index.js';

	// Props using $props() for Svelte 5 runes mode
	const props = $props<{
		currentPage: number;
		totalPages: number;
		pageSize: number;
	}>();

	const dispatch = createEventDispatcher();

	function goToPage(page: number) {
		dispatch('setPage', page);
	}

	function goToPreviousPage() {
		dispatch('previous');
	}

	function goToNextPage() {
		dispatch('next');
	}

	// Watch for changes to pageSize
	let pageSize = $state(props.pageSize);

	$effect(() => {
		if (pageSize !== props.pageSize) {
			pageSize = props.pageSize;
		}
	});

	$effect(() => {
		if (pageSize) {
			dispatch('setPageSize', pageSize);
		}
	});
</script>

<div class="mt-4 flex items-center justify-between">
	<div class="flex items-center dark:text-gray-300">
		<Label for="page-size" class="mr-2">Rows per page:</Label>
		<Select.Root type="single" bind:value={pageSize} id="page-size">
			<Select.Trigger class="w-20">
				{pageSize}
			</Select.Trigger>
			<Select.Content>
				<Select.Item value={5}>5</Select.Item>
				<Select.Item value={10}>10</Select.Item>
				<Select.Item value={20}>20</Select.Item>
			</Select.Content>
		</Select.Root>
	</div>
	<div class="text-gray-700 dark:text-gray-300">
		Page {props.currentPage} of {props.totalPages}
	</div>
	<div class="space-x-2">
		<Button
			variant="outline"
			size="sm"
			onclick={goToPreviousPage}
			disabled={props.currentPage <= 1}
		>
			Prev
		</Button>
		<Button
			variant="outline"
			size="sm"
			onclick={goToNextPage}
			disabled={props.currentPage >= props.totalPages}
		>
			Next
		</Button>
	</div>
</div>
