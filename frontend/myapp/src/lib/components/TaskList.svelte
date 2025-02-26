<script lang="ts">
  import { onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Textarea } from "$lib/components/ui/textarea";
  
  // Define the shape of a Task
  interface Task {
    id: number;
    title: string;
    description?: string;
    status?: string;
    priority?: string;
  }

  let tasks: Task[] = [];
  let loading = true;
  let error: string | null = null;

  // Controls for the "Add new task" form
  let newTask: Task = {
    id: 0,
    title: '',
    description: '',
    status: '',
    priority: ''
  };
  let showAddForm = false;

  // Controls for editing
  let editingTask: Task | null = null;

  // Filtering and search
  let searchQuery = '';
  let statusFilter = '';
  let priorityFilter = '';

  // Sorting
  let sortField: keyof Task = 'title';
  let sortDirection: 'asc' | 'desc' = 'asc';

  // Pagination
  let currentPage = 1;
  let pageSize = 10;

  // Fetch all tasks
  async function fetchTasks() {
    loading = true;
    try {
      const response = await fetch('/tasks');
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      tasks = await response.json();
    } catch (err: any) {
      error = err.message;
      console.error('Error fetching tasks:', err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchTasks();
  });

  // Derived tasks after filter + sort + pagination
  $: filteredSortedTasks = tasks
    // 1) filter by search and status/priority
    .filter(task => {
      const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter ? task.status === statusFilter : true;
      const matchesPriority = priorityFilter ? task.priority === priorityFilter : true;
      return matchesSearch && matchesStatus && matchesPriority;
    })
    // 2) sort by the chosen field/direction
    .sort((a, b) => {
      const valA = (a[sortField] || '').toString().toLowerCase();
      const valB = (b[sortField] || '').toString().toLowerCase();
      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

  // 3) slice for pagination
  $: totalItems = filteredSortedTasks.length;
  $: totalPages = Math.ceil(totalItems / pageSize);
  $: paginatedTasks = filteredSortedTasks.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

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
      // After adding, refetch tasks (or push to tasks array if your backend returns the new record)
      await fetchTasks();
      newTask = { id: 0, title: '', description: '', status: '', priority: '' };
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
    } catch (err: any) {
      error = err.message;
      console.error('Error deleting task:', err);
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
  async function saveEdit() {
    if (!editingTask) return;
    try {
      const response = await fetch(`/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingTask)
      });
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

      // Update the local array
      tasks = tasks.map(task => (task.id === editingTask!.id ? editingTask! : task));
      editingTask = null;
    } catch (err: any) {
      error = err.message;
      console.error('Error updating task:', err);
    }
  }

  // Handle pagination
  function goToPage(page: number) {
    currentPage = page;
  }
  function goToPreviousPage() {
    if (currentPage > 1) currentPage--;
  }
  function goToNextPage() {
    if (currentPage < totalPages) currentPage++;
  }

  // Toggle sorting
  function setSort(field: keyof Task) {
    if (sortField === field) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortField = field;
      sortDirection = 'asc';
    }
  }
</script>

<main class="p-6 max-w-6xl mx-auto">
  <!-- Heading -->
  <div class="mb-6">
    <h1 class="text-2xl font-bold text-slate-800">Welcome back!</h1>
    <p class="text-gray-600">Here's a list of your tasks for this month!</p>
  </div>

  <!-- Error Alert -->
  {#if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 flex justify-between items-center">
      <p>Error: {error}</p>
      <Button variant="link" on:click={() => error = null}>Dismiss</Button>
    </div>
  {/if}

  <!-- Filter and Add Task Bar -->
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
    <div class="flex gap-2">
      <Input
        placeholder="Filter tasks..."
        class="w-48"
        bind:value={searchQuery}
      />
      <select
        class="border border-gray-300 rounded px-2 py-1"
        bind:value={statusFilter}
      >
        <option value="">All Statuses</option>
        <option value="Bug">Bug</option>
        <option value="Feature">Feature</option>
        <option value="Documentation">Documentation</option>
        <option value="In Progress">In Progress</option>
        <!-- etc. -->
      </select>
      <select
        class="border border-gray-300 rounded px-2 py-1"
        bind:value={priorityFilter}
      >
        <option value="">All Priorities</option>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
      </select>
    </div>
    <div>
      {#if !showAddForm}
        <Button on:click={() => showAddForm = true}>Add New Task</Button>
      {/if}
    </div>
  </div>

  <!-- Add Task Form -->
  {#if showAddForm}
    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
      <h2 class="text-lg font-semibold mb-2">Add New Task</h2>
      <form on:submit|preventDefault={addTask}>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Title</label>
            <Input
              type="text"
              bind:value={newTask.title}
              placeholder="Task title"
              required
              class="mt-1 w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <Input
              type="text"
              bind:value={newTask.status}
              placeholder="e.g. Bug, Feature..."
              class="mt-1 w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Priority</label>
            <Input
              type="text"
              bind:value={newTask.priority}
              placeholder="e.g. High, Medium, Low"
              class="mt-1 w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <Textarea
              bind:value={newTask.description}
              placeholder="Task description"
              rows="3"
              class="mt-1 w-full"
            />
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-4">
          <Button type="submit">Save Task</Button>
          <Button variant="secondary" type="button" on:click={() => showAddForm = false}>Cancel</Button>
        </div>
      </form>
    </div>
  {/if}

  <!-- Loading / No tasks states -->
  {#if loading}
    <div class="text-center text-gray-500 italic">Loading tasks...</div>
  {:else if tasks.length === 0}
    <div class="text-center text-gray-500 py-10">No tasks found. Create your first task!</div>
  {:else}
    <!-- Table -->
    <div class="overflow-x-auto border border-gray-200 rounded-lg">
      <table class="min-w-full text-left bg-white">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th
              class="px-4 py-2 cursor-pointer"
              on:click={() => setSort('title')}
            >
              Title
              {#if sortField === 'title'}
                {sortDirection === 'asc' ? ' ▲' : ' ▼'}
              {/if}
            </th>
            <th
              class="px-4 py-2 cursor-pointer"
              on:click={() => setSort('status')}
            >
              Status
              {#if sortField === 'status'}
                {sortDirection === 'asc' ? ' ▲' : ' ▼'}
              {/if}
            </th>
            <th
              class="px-4 py-2 cursor-pointer"
              on:click={() => setSort('priority')}
            >
              Priority
              {#if sortField === 'priority'}
                {sortDirection === 'asc' ? ' ▲' : ' ▼'}
              {/if}
            </th>
            <th class="px-4 py-2">Description</th>
            <th class="px-4 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each paginatedTasks as task}
            <tr class="border-b border-gray-100 hover:bg-gray-50">
              {#if editingTask && editingTask.id === task.id}
                <!-- Edit Row -->
                <td class="px-4 py-2" colspan="5">
                  <div class="grid md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Title</label>
                      <Input
                        type="text"
                        bind:value={editingTask.title}
                        required
                        class="mt-1 w-full"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Status</label>
                      <Input
                        type="text"
                        bind:value={editingTask.status}
                        class="mt-1 w-full"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Priority</label>
                      <Input
                        type="text"
                        bind:value={editingTask.priority}
                        class="mt-1 w-full"
                      />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Description</label>
                      <Textarea
                        bind:value={editingTask.description}
                        rows="3"
                        class="mt-1 w-full"
                      />
                    </div>
                  </div>
                  <div class="flex justify-end space-x-2 mt-4">
                    <Button on:click={saveEdit}>Save</Button>
                    <Button variant="secondary" on:click={cancelEdit}>Cancel</Button>
                  </div>
                </td>
              {:else}
                <!-- Display Row -->
                <td class="px-4 py-2">{task.title}</td>
                <td class="px-4 py-2">{task.status}</td>
                <td class="px-4 py-2">{task.priority}</td>
                <td class="px-4 py-2">
                  {task.description}
                </td>
                <td class="px-4 py-2 text-right">
                  <Button variant="secondary" size="sm" on:click={() => startEdit(task)}>Edit</Button>
                  <Button variant="destructive" size="sm" class="ml-2" on:click={() => deleteTask(task.id)}>Delete</Button>
                </td>
              {/if}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between mt-2">
      <div>
        Rows per page:
        <select
          class="border border-gray-300 rounded px-2 py-1 ml-1"
          bind:value={pageSize}
          on:change={() => currentPage = 1}
        >
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="20">20</option>
        </select>
      </div>
      <div class="text-gray-700">
        Page {currentPage} of {totalPages}
      </div>
      <div class="space-x-2">
        <Button variant="secondary" on:click={goToPreviousPage} disabled={currentPage === 1}>
          Prev
        </Button>
        <Button variant="secondary" on:click={goToNextPage} disabled={currentPage === totalPages}>
          Next
        </Button>
      </div>
    </div>
  {/if}
</main>
