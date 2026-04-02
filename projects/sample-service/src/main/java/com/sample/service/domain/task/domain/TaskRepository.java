package com.sample.service.domain.task.domain;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface TaskRepository {
    List<Task> findAll();

    Optional<Task> findById(UUID id);

    Task save(Task task);

    void deleteById(UUID id);
}
