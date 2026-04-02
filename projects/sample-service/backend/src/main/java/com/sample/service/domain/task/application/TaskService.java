package com.sample.service.domain.task.application;

import com.sample.service.common.enums.TaskStatus;
import com.sample.service.domain.task.domain.Task;
import com.sample.service.domain.task.domain.TaskRepository;
import com.sample.service.global.exception.TaskNotFoundException;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class TaskService {
    private final TaskRepository taskRepository;
    private final Clock clock;

    public TaskService(TaskRepository taskRepository, Clock clock) {
        this.taskRepository = taskRepository;
        this.clock = clock;
    }

    public List<Task> listTasks() {
        return taskRepository.findAll();
    }

    public Task getTask(UUID id) {
        return taskRepository.findById(id).orElseThrow(() -> new TaskNotFoundException(id));
    }

    public Task createTask(String title, String description) {
        Instant now = Instant.now(clock);
        Task task = new Task(UUID.randomUUID(), title, description, TaskStatus.PENDING, now, now);
        return taskRepository.save(task);
    }

    public Task updateTaskStatus(UUID id, TaskStatus status) {
        Task existing = getTask(id);
        Task updated = new Task(
                existing.getId(),
                existing.getTitle(),
                existing.getDescription(),
                status,
                existing.getCreatedAt(),
                Instant.now(clock)
        );
        return taskRepository.save(updated);
    }

    public void deleteTask(UUID id) {
        if (taskRepository.findById(id).isEmpty()) {
            throw new TaskNotFoundException(id);
        }
        taskRepository.deleteById(id);
    }
}
