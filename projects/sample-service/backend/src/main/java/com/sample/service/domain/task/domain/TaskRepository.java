package com.sample.service.domain.task.domain;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface TaskRepository {
    Task save(Task task);

    List<Task> findAll();

    Optional<Task> findById(UUID id);

    void deleteById(UUID id);
}
