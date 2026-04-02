package com.sample.service.domain.task.application;

import com.sample.service.common.config.TaskProperties;
import com.sample.service.common.enums.TaskStatus;
import com.sample.service.domain.task.domain.Task;
import com.sample.service.domain.task.domain.TaskRepository;
import com.sample.service.global.exception.InputValidationException;
import com.sample.service.global.exception.TaskNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.UUID;

@Service
public class TaskService {

    private final TaskRepository taskRepository;
    private final TaskProperties taskProperties;

    public TaskService(TaskRepository taskRepository, TaskProperties taskProperties) {
        this.taskRepository = taskRepository;
        this.taskProperties = taskProperties;
    }

    public List<Task> getTasks() {
        return taskRepository.findAll().stream()
                .sorted(Comparator.comparing(Task::id))
                .toList();
    }

    public Task getTask(UUID id) {
        return taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));
    }

    public Task createTask(String title) {
        String normalizedTitle = normalizeTitle(title);
        Task task = new Task(UUID.randomUUID(), normalizedTitle, TaskStatus.PENDING);
        return taskRepository.save(task);
    }

    public Task updateStatus(UUID id, TaskStatus status) {
        Task existing = getTask(id);
        Task updated = new Task(existing.id(), existing.title(), status);
        return taskRepository.save(updated);
    }

    public void deleteTask(UUID id) {
        if (!taskRepository.deleteById(id)) {
            throw new TaskNotFoundException(id);
        }
    }

    private String normalizeTitle(String title) {
        String normalized = title == null ? "" : title.trim();
        if (normalized.isEmpty()) {
            throw new InputValidationException("title must not be blank");
        }
        if (normalized.length() > taskProperties.titleMaxLength()) {
            throw new InputValidationException(
                    "title length must be less than or equal to " + taskProperties.titleMaxLength());
        }
        return normalized;
    }
}
