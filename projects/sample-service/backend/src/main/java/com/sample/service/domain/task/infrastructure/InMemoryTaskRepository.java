package com.sample.service.domain.task.infrastructure;

import com.sample.service.domain.task.domain.Task;
import com.sample.service.domain.task.domain.TaskRepository;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Repository;

@Repository
@ConditionalOnProperty(name = "app.task.repository", havingValue = "memory")
public class InMemoryTaskRepository implements TaskRepository {
    private final Map<UUID, Task> store = new ConcurrentHashMap<>();

    @Override
    public Task save(Task task) {
        store.put(task.getId(), task);
        return task;
    }

    @Override
    public List<Task> findAll() {
        return store.values().stream()
                .sorted(Comparator.comparing(Task::getCreatedAt).thenComparing(Task::getId))
                .toList();
    }

    @Override
    public Optional<Task> findById(UUID id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public void deleteById(UUID id) {
        store.remove(id);
    }
}
