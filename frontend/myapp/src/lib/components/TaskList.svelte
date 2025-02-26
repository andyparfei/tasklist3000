<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import Muuri from 'muuri';
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Textarea } from "$lib/components/ui/textarea";

  let tasks = [];
  let loading = true;
  let error: string | null = null;
  let newTask = { title: '', description: '' };
  let editingTask = null;
  let showAddForm = false;
  let grid: Muuri; // Muuri grid instance

  // Fetch all tasks
  async function fetchTasks() {
    loading = true;
    try {
      const response = await fetch('/tasks');
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      tasks = await response.json();
      // Refresh Muuri layout after tasks are loaded
      setTimeout(() => {
        if (grid) {
          grid.refreshItems();
          grid.layout();
        }
      }, 0);
    } catch (err: any) {
      error = err.message;
      console.error('Error fetching tasks:', err);
    } finally {
      loading = false;
    }
  }

  // Add a new task
  async function addTask() {
    if (!newTask.title.trim()) return;
    try {
      const response = await fetch('/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask)
      });
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      await fetchTasks();
      newTask = { title: '', description: '' };
      showAddForm = false;
    } catch (err: any) {
      error = err.message;
      console.error('Error adding task:', err);
    }
  }

  // Delete a task
  async function deleteTask(id: number) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      const response = await fetch(`/tasks/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      tasks = tasks.filter(task => task.id !== id);
      if (grid) {
        const itemsToRemove = grid.getItems().filter(
          item => item.getElement().dataset.id === id.toString()
        );
        grid.remove(itemsToRemove, { removeElements: true });
      }
    } catch (err: any) {
      error = err.message;
      console.error('Error deleting task:', err);
    }
  }

  // Start editing a task
  function startEdit(task) {
    editingTask = { ...task };
  }

  // Cancel editing
  function cancelEdit() {
    editingTask = null;
  }

  // Save edited task
  async function saveEdit() {
    try {
      const response = await fetch(`/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editingTask.title,
          description: editingTask.description
        })
      });
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      tasks = tasks.map(task =>
        task.id === editingTask.id ? editingTask : task
      );
      editingTask = null;
    } catch (err: any) {
      error = err.message;
      console.error('Error updating task:', err);
    }
  }

  // Update tasks order based on Muuri’s new order
  function updateTaskOrder() {
    const newOrder = grid.getItems().map(item => item.getElement().dataset.id);
    tasks = newOrder.map(id =>
      tasks.find(task => task.id.toString() === id)
    );
  }

  onMount(() => {
    fetchTasks();
    // Wait for the task items to render before initializing Muuri
    setTimeout(() => {
      grid = new Muuri('.task-list', {
        dragEnabled: true,
        layoutDuration: 400,
        layoutEasing: 'ease'
      });
      grid.on('dragEnd', updateTaskOrder);
    }, 100);
  });

  // Refresh the Muuri grid after each update
  afterUpdate(() => {
    if (grid) {
      grid.refreshItems();
      grid.layout();
    }
  });
</script>

<main class="p-6 max-w-4xl mx-auto">
  <div class="bg-white shadow-lg rounded-lg p-8">
    <h1 class="text-3xl font-bold text-center text-slate-600 mb-6">TaskList 3000</h1>

    {#if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 flex justify-between items-center">
        <p>Error: {error}</p>
        <Button variant="link" on:click={() => error = null}>Dismiss</Button>
      </div>
    {/if}

    <div class="flex justify-end mb-4">
      {#if !showAddForm}
        <Button on:click={() => showAddForm = true}>Add New Task</Button>
      {/if}
    </div>

    {#if showAddForm}
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Add New Task</h2>
        <form on:submit|preventDefault={addTask}>
          <div class="mb-4">
            <label for="title" class="block text-sm font-medium text-gray-700">Title</label>
            <Input id="title" type="text" bind:value={newTask.title} placeholder="Task title" required class="mt-1 block w-full"/>
          </div>
          <div class="mb-4">
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <Textarea id="description" bind:value={newTask.description} placeholder="Task description" rows="3" class="mt-1 block w-full"/>
          </div>
          <div class="flex justify-end space-x-2">
            <Button type="submit">Save Task</Button>
            <Button variant="secondary" type="button" on:click={() => showAddForm = false}>Cancel</Button>
          </div>
        </form>
      </div>
    {/if}

    {#if loading}
      <div class="text-center text-gray-500 italic">Loading tasks...</div>
    {:else if tasks.length === 0}
      <div class="text-center text-gray-500 py-10">No tasks found. Create your first task!</div>
    {:else}
      <!-- Muuri grid container -->
      <div class="task-list grid grid-cols-1 gap-4">
        {#each tasks as task (task.id)}
          <div class="task-item bg-white border border-gray-200 rounded-lg p-4 shadow hover:shadow-md" data-id={task.id}>
            {#if editingTask && editingTask.id === task.id}
              <div class="edit-form">
                <div class="mb-4">
                  <label for="edit-title" class="block text-sm font-medium text-gray-700">Title</label>
                  <Input id="edit-title" type="text" bind:value={editingTask.title} required class="mt-1 block w-full"/>
                </div>
                <div class="mb-4">
                  <label for="edit-description" class="block text-sm font-medium text-gray-700">Description</label>
                  <Textarea id="edit-description" bind:value={editingTask.description} rows="3" class="mt-1 block w-full"/>
                </div>
                <div class="flex justify-end space-x-2">
                  <Button on:click={saveEdit}>Save</Button>
                  <Button variant="secondary" on:click={cancelEdit}>Cancel</Button>
                </div>
              </div>
            {:else}
              <div class="task-content">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-gray-800">{task.title}</h3>
                  <!-- Drag handle (using an icon) -->
                  <div class="drag-handle cursor-move text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4 5a1 1 0 112 0 1 1 0 11-2 0zm0 4a1 1 0 112 0 1 1 0 11-2 0zm0 4a1 1 0 112 0 1 1 0 11-2 0zm4-8a1 1 0 112 0 1 1 0 11-2 0zm0 4a1 1 0 112 0 1 1 0 11-2 0zm0 4a1 1 0 112 0 1 1 0 11-2 0zm4-8a1 1 0 112 0 1 1 0 11-2 0zm0 4a1 1 0 112 0 1 1 0 11-2 0zm0 4a1 1 0 112 0 1 1 0 11-2 0z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>
                {#if task.description}
                  <p class="text-gray-600 mt-2">{task.description}</p>
                {/if}
                <div class="flex justify-end mt-4 space-x-2">
                  <Button variant="secondary" on:click={() => startEdit(task)}>Edit</Button>
                  <Button variant="destructive" on:click={() => deleteTask(task.id)}>Delete</Button>
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>
