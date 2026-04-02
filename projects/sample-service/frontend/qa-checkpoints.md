STEP_LABEL: frontend
AGENT: frontend
PHASE: base
FEEDBACK_ROUND: 1
STATUS: needs-review

# Frontend QA Checkpoints

## State and UX Rules
- Loading: show `Loading tasks...` while list request is pending.
- Empty: show `No tasks yet. Create your first task.` when list returns 0 items.
- Detail loading: show `Loading detail...` while `GET /api/v1/tasks/{id}` is pending.
- Error: surface API `error.message` from payload and render it in the feedback area.
- Success feedback:
  - create success -> `Task created`
  - status update success -> `Task status updated`
  - delete success -> `Task deleted`
- Delete API handling: `DELETE` expects `204` and must not parse JSON body.

## Manual Smoke Checklist
1. Create task with valid title and optional description; verify list/detail refresh and status is `PENDING`.
2. Create task with blank title; verify validation error is visible.
3. Select an existing task and verify detail pane values are shown.
4. Change status from `PENDING` to `DONE`; verify list badge and detail status update.
5. Attempt invalid status via API replay (or backend test); verify readable error message.
6. Delete task; verify row disappears and subsequent detail fetch results in not-found handling.
7. Simulate backend off/down; verify feedback area shows API failure message.
8. Verify keyboard navigation: tab focus reaches form fields, list item buttons, action buttons, and refresh.
9. Verify responsive layout at mobile width (`<=1040px`): panels stack and remain readable.

## Review Agent Handoff Risks
- Risk: runtime connectivity may fail if proxy target differs from runtime network topology.
- Risk: backend returns non-JSON error payload in some edge cases; UI currently falls back to `Request failed (status)`.
- Risk: no automated frontend tests yet; current validation is manual checklist centric.
