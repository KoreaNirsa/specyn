package com.sample.service.domain.task.infrastructure;

import com.sample.service.domain.task.domain.Task;
import com.sample.service.domain.task.domain.TaskRepository;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Repository
public class InMemoryTaskRepository implements TaskRepository {

    private final Map<UUID, Task> storage = new LinkedHashMap<>();

    @Override
    public synchronized List<Task> findAll() {
        return new ArrayList<>(storage.values());
    }

    @Override
    public synchronized Optional<Task> findById(UUID id) {
        return Optional.ofNullable(storage.get(id));
    }

    @Override
    public synchronized Task save(Task task) {
        storage.put(task.id(), task);
        return task;
    }

    @Override
    public synchronized void deleteById(UUID id) {
        storage.remove(id);
    }
}
