-- Manual rollback for V1__create_tasks.sql
-- WARNING: this is destructive and permanently removes all task data.
DROP INDEX IF EXISTS idx_tasks_created_at_id;
DROP TABLE IF EXISTS tasks;
