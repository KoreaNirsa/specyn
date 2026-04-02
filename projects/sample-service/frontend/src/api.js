const API_BASE = (import.meta.env.VITE_API_BASE || '/api/v1/tasks').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const fallback = `Request failed (${response.status})`;
    const message = payload?.message || fallback;
    const error = new Error(message);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

export async function listTasks() {
  const payload = await request('', { method: 'GET' });
  return payload?.items || [];
}

export async function getTask(id) {
  const payload = await request(`/${id}`, { method: 'GET' });
  return payload?.data || null;
}

export async function createTask(input) {
  const payload = await request('', {
    method: 'POST',
    body: JSON.stringify(input)
  });
  return payload?.data || null;
}

export async function updateTaskStatus(id, status) {
  const payload = await request(`/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
  return payload?.data || null;
}

export async function deleteTask(id) {
  await request(`/${id}`, { method: 'DELETE' });
}
