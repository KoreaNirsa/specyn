CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    status VARCHAR(16) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT ck_tasks_title_not_blank CHECK (TRIM(title) <> ''),
    CONSTRAINT ck_tasks_status CHECK (status IN ('PENDING', 'DONE')),
    CONSTRAINT ck_tasks_updated_gte_created CHECK (updated_at >= created_at)
);

CREATE INDEX IF NOT EXISTS idx_tasks_created_at_id
    ON tasks (created_at ASC, id ASC);
