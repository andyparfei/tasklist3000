<script>
  import { onMount } from 'svelte';

  let tasks = [];
  let loading = true;
  let error = null;
  let newTask = { title: '', description: '' };
  let editingTask = null;
  let showAddForm = false;

  // Fetch all tasks
  async function fetchTasks() {
    loading = true;
    try {
      const response = await fetch('/tasks');
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      tasks = await response.json();
    } catch (err) {
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
    } catch (err) {
      error = err.message;
      console.error('Error adding task:', err);
    }
  }

  // Delete a task
  async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
      const response = await fetch(`/tasks/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      tasks = tasks.filter(task => task.id !== id);
    } catch (err) {
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
    } catch (err) {
      error = err.message;
      console.error('Error updating task:', err);
    }
  }

  onMount(fetchTasks);
</script>

<main>
  <div class="container">
    <h1>TaskList 3000</h1>
    
    {#if error}
      <div class="error-banner">
        <p>Error: {error}</p>
        <button on:click={() => error = null}>Dismiss</button>
      </div>
    {/if}
    
    <div class="actions">
      {#if !showAddForm}
        <button class="btn-primary" on:click={() => showAddForm = true}>Add New Task</button>
      {/if}
    </div>
    
    {#if showAddForm}
      <div class="form-container">
        <h2>Add New Task</h2>
        <form on:submit|preventDefault={addTask}>
          <div class="form-group">
            <label for="title">Title</label>
            <input 
              id="title"
              type="text" 
              bind:value={newTask.title} 
              placeholder="Task title" 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="description">Description</label>
            <textarea 
              id="description"
              bind:value={newTask.description} 
              placeholder="Task description"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn-primary">Save Task</button>
            <button type="button" class="btn-secondary" on:click={() => showAddForm = false}>Cancel</button>
          </div>
        </form>
      </div>
    {/if}
    
    {#if loading}
      <div class="loading">Loading tasks...</div>
    {:else if tasks.length === 0}
      <div class="empty-state">
        <p>No tasks found. Create your first task!</p>
      </div>
    {:else}
      <ul class="task-list">
        {#each tasks as task (task.id)}
          <li class="task-item">
            {#if editingTask && editingTask.id === task.id}
              <div class="edit-form">
                <div class="form-group">
                  <label for="edit-title">Title</label>
                  <input 
                    id="edit-title"
                    type="text" 
                    bind:value={editingTask.title} 
                    required
                  />
                </div>
                
                <div class="form-group">
                  <label for="edit-description">Description</label>
                  <textarea 
                    id="edit-description"
                    bind:value={editingTask.description} 
                    rows="3"
                  ></textarea>
                </div>
                
                <div class="item-actions">
                  <button on:click={saveEdit} class="btn-primary">Save</button>
                  <button on:click={cancelEdit} class="btn-secondary">Cancel</button>
                </div>
              </div>
            {:else}
              <div class="task-content">
                <h3>{task.title}</h3>
                {#if task.description}
                  <p>{task.description}</p>
                {/if}
                
                <div class="item-actions">
                  <button on:click={() => startEdit(task)} class="btn-secondary">Edit</button>
                  <button on:click={() => deleteTask(task.id)} class="btn-danger">Delete</button>
                </div>
              </div>
            {/if}
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</main>

<style>
  main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 30px;
  }
  
  h1 {
    color: #2563eb;
    margin-top: 0;
    text-align: center;
    margin-bottom: 30px;
  }
  
  .actions {
    margin-bottom: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .btn-primary {
    background-color: #2563eb;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  .btn-primary:hover {
    background-color: #1d4ed8;
  }
  
  .btn-secondary {
    background-color: #f3f4f6;
    color: #4b5563;
    border: 1px solid #d1d5db;
    padding: 9px 15px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 10px;
    transition: background-color 0.2s;
  }
  
  .btn-secondary:hover {
    background-color: #e5e7eb;
  }
  
  .btn-danger {
    background-color: #ef4444;
    color: white;
    border: none;
    padding: 9px 15px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 10px;
    transition: background-color 0.2s;
  }
  
  .btn-danger:hover {
    background-color: #dc2626;
  }
  
  .form-container {
    background-color: #f9fafb;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 25px;
    border: 1px solid #e5e7eb;
  }
  
  .form-container h2 {
    margin-top: 0;
    font-size: 1.25rem;
    color: #1f2937;
    margin-bottom: 20px;
  }
  
  .form-group {
    margin-bottom: 16px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: #4b5563;
  }
  
  input[type="text"], textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
  }
  
  input[type="text"]:focus, textarea:focus {
    outline: none;
    border-color: #93c5fd;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  
  .task-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .task-item {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    margin-bottom: 15px;
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
  }
  
  .task-item:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
  
  .task-content {
    padding: 20px;
  }
  
  .task-content h3 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #1f2937;
  }
  
  .task-content p {
    color: #6b7280;
    margin-top: 0;
    margin-bottom: 15px;
  }
  
  .item-actions {
    display: flex;
    justify-content: flex-end;
  }
  
  .edit-form {
    padding: 20px;
  }
  
  .loading {
    text-align: center;
    padding: 30px;
    color: #6b7280;
    font-style: italic;
  }
  
  .empty-state {
    text-align: center;
    padding: 40px 0;
    color: #6b7280;
  }
  
  .error-banner {
    background-color: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .error-banner p {
    margin: 0;
    color: #b91c1c;
  }
  
  .error-banner button {
    background: none;
    border: none;
    color: #b91c1c;
    font-weight: 500;
    cursor: pointer;
    padding: 0;
    font-size: 0.875rem;
  }
</style>