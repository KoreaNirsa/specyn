package com.sample.service.domain.task.infrastructure;

import com.sample.service.common.enums.TaskStatus;
import com.sample.service.domain.task.domain.Task;
import com.sample.service.domain.task.domain.TaskRepository;
import java.sql.Timestamp;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
@ConditionalOnProperty(name = "app.task.repository", havingValue = "jdbc", matchIfMissing = true)
public class JdbcTaskRepository implements TaskRepository {
    private final JdbcTemplate jdbcTemplate;

    public JdbcTaskRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public Task save(Task task) {
        int updated = jdbcTemplate.update(
                "UPDATE tasks SET title = ?, description = ?, status = ?, created_at = ?, updated_at = ? WHERE id = ?",
                task.getTitle(),
                task.getDescription(),
                task.getStatus().name(),
                Timestamp.from(task.getCreatedAt()),
                Timestamp.from(task.getUpdatedAt()),
                task.getId()
        );

        if (updated == 0) {
            jdbcTemplate.update(
                    "INSERT INTO tasks (id, title, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    task.getId(),
                    task.getTitle(),
                    task.getDescription(),
                    task.getStatus().name(),
                    Timestamp.from(task.getCreatedAt()),
                    Timestamp.from(task.getUpdatedAt())
            );
        }

        return task;
    }

    @Override
    public List<Task> findAll() {
        return jdbcTemplate.query(
                "SELECT id, title, description, status, created_at, updated_at FROM tasks ORDER BY created_at, id",
                (rs, rowNum) -> new Task(
                        rs.getObject("id", UUID.class),
                        rs.getString("title"),
                        rs.getString("description"),
                        TaskStatus.valueOf(rs.getString("status")),
                        rs.getTimestamp("created_at").toInstant(),
                        rs.getTimestamp("updated_at").toInstant()
                )
        );
    }

    @Override
    public Optional<Task> findById(UUID id) {
        List<Task> rows = jdbcTemplate.query(
                "SELECT id, title, description, status, created_at, updated_at FROM tasks WHERE id = ?",
                (rs, rowNum) -> new Task(
                        rs.getObject("id", UUID.class),
                        rs.getString("title"),
                        rs.getString("description"),
                        TaskStatus.valueOf(rs.getString("status")),
                        rs.getTimestamp("created_at").toInstant(),
                        rs.getTimestamp("updated_at").toInstant()
                ),
                id
        );
        return rows.stream().findFirst();
    }

    @Override
    public void deleteById(UUID id) {
        jdbcTemplate.update("DELETE FROM tasks WHERE id = ?", id);
    }
}
