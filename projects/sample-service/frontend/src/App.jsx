import React, { useEffect, useMemo, useState } from 'react';
import {
  createTask,
  deleteTask,
  getTask,
  listTasks,
  updateTaskStatus
} from './api.js';

const STATUS_VALUES = ['PENDING', 'DONE'];

function formatTimestamp(value) {
  if (!value) {
    return '-';
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const [listLoading, setListLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const canSubmit = useMemo(() => title.trim().length > 0 && title.trim().length <= 200, [title]);

  useEffect(() => {
    void loadTasks();
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setSelectedTask(null);
      return;
    }

    void loadTaskDetail(selectedId);
  }, [selectedId]);

  async function loadTasks() {
    setListLoading(true);
    try {
      const items = await listTasks();
      setTasks(items);

      if (items.length === 0) {
        setSelectedId(null);
        return;
      }

      if (!selectedId || !items.some((task) => task.id === selectedId)) {
        setSelectedId(items[0].id);
      }
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setListLoading(false);
    }
  }

  async function loadTaskDetail(id) {
    setDetailLoading(true);
    try {
      const detail = await getTask(id);
      setSelectedTask(detail);
    } catch (error) {
      setErrorMessage(error.message);
      setSelectedTask(null);
    } finally {
      setDetailLoading(false);
    }
  }

  async function onCreateTask(event) {
    event.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    const safeTitle = title.trim();
    const safeDescription = description.trim();

    if (!safeTitle) {
      setErrorMessage('title is required');
      return;
    }

    setCreating(true);
    try {
      const created = await createTask({
        title: safeTitle,
        description: safeDescription || null
      });

      setTitle('');
      setDescription('');
      setSuccessMessage('Task created');

      await loadTasks();
      if (created?.id) {
        setSelectedId(created.id);
      }
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setCreating(false);
    }
  }

  async function onToggleStatus(task) {
    const nextStatus = task.status === 'DONE' ? 'PENDING' : 'DONE';
    if (!STATUS_VALUES.includes(nextStatus)) {
      return;
    }

    setErrorMessage('');
    setSuccessMessage('');
    setUpdatingId(task.id);

    try {
      await updateTaskStatus(task.id, nextStatus);
      setSuccessMessage('Task status updated');
      await loadTasks();
      if (selectedId === task.id) {
        await loadTaskDetail(task.id);
      }
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setUpdatingId(null);
    }
  }

  async function onDeleteTask(taskId) {
    setErrorMessage('');
    setSuccessMessage('');
    setDeletingId(taskId);

    try {
      await deleteTask(taskId);
      setSuccessMessage('Task deleted');

      const nextSelection = selectedId === taskId ? null : selectedId;
      setSelectedId(nextSelection);
      await loadTasks();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="app-shell">
      <section className="panel panel-create" aria-labelledby="create-task-heading">
        <h1 id="create-task-heading">Task Console</h1>
        <p className="panel-description">Create and manage tasks with explicit API feedback.</p>

        <form onSubmit={onCreateTask} className="task-form">
          <label htmlFor="task-title">Title</label>
          <input
            id="task-title"
            name="title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            maxLength={200}
            required
            placeholder="Write deployment guide"
          />

          <label htmlFor="task-description">Description</label>
          <textarea
            id="task-description"
            name="description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            maxLength={2000}
            rows={4}
            placeholder="Optional details"
          />

          <button type="submit" disabled={!canSubmit || creating}>
            {creating ? 'Creating...' : 'Create Task'}
          </button>
        </form>

        <div className="feedback-zone" aria-live="polite">
          {successMessage ? <p className="feedback success">{successMessage}</p> : null}
          {errorMessage ? <p className="feedback error">{errorMessage}</p> : null}
        </div>
      </section>

      <section className="panel panel-list" aria-labelledby="task-list-heading">
        <div className="panel-header">
          <h2 id="task-list-heading">Tasks</h2>
          <button type="button" onClick={() => void loadTasks()} disabled={listLoading}>
            {listLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {listLoading ? (
          <p className="state state-loading">Loading tasks...</p>
        ) : tasks.length === 0 ? (
          <p className="state state-empty">No tasks yet. Create your first task.</p>
        ) : (
          <ul className="task-list" aria-label="Task list">
            {tasks.map((task) => {
              const isSelected = selectedId === task.id;
              const isUpdating = updatingId === task.id;
              const isDeleting = deletingId === task.id;

              return (
                <li key={task.id} className={isSelected ? 'selected' : ''}>
                  <button
                    type="button"
                    className="task-select"
                    onClick={() => setSelectedId(task.id)}
                    aria-current={isSelected ? 'true' : 'false'}
                  >
                    <span className="task-title">{task.title}</span>
                    <span className={`task-status status-${task.status.toLowerCase()}`}>{task.status}</span>
                  </button>

                  <div className="task-actions">
                    <button type="button" onClick={() => void onToggleStatus(task)} disabled={isUpdating || isDeleting}>
                      {isUpdating ? 'Saving...' : task.status === 'DONE' ? 'Mark PENDING' : 'Mark DONE'}
                    </button>
                    <button type="button" onClick={() => void onDeleteTask(task.id)} disabled={isDeleting || isUpdating}>
                      {isDeleting ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section className="panel panel-detail" aria-labelledby="task-detail-heading">
        <h2 id="task-detail-heading">Task Detail</h2>
        {!selectedId ? (
          <p className="state state-empty">Select a task to view detail.</p>
        ) : detailLoading ? (
          <p className="state state-loading">Loading detail...</p>
        ) : !selectedTask ? (
          <p className="state state-error">Task detail unavailable.</p>
        ) : (
          <dl className="task-detail">
            <div>
              <dt>ID</dt>
              <dd>{selectedTask.id}</dd>
            </div>
            <div>
              <dt>Title</dt>
              <dd>{selectedTask.title}</dd>
            </div>
            <div>
              <dt>Description</dt>
              <dd>{selectedTask.description || '-'}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{selectedTask.status}</dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>{formatTimestamp(selectedTask.createdAt)}</dd>
            </div>
            <div>
              <dt>Updated</dt>
              <dd>{formatTimestamp(selectedTask.updatedAt)}</dd>
            </div>
          </dl>
        )}
      </section>
    </main>
  );
}
