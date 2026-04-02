package com.sample.service.domain.task.api;

import com.sample.service.domain.task.api.dto.CreateTaskRequest;
import com.sample.service.domain.task.api.dto.TaskDto;
import com.sample.service.domain.task.api.dto.TaskListResponse;
import com.sample.service.domain.task.api.dto.TaskResponse;
import com.sample.service.domain.task.api.dto.UpdateTaskStatusRequest;
import com.sample.service.domain.task.application.TaskService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/tasks")
public class TaskController {
    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping
    public TaskListResponse listTasks() {
        List<TaskDto> items = taskService.listTasks().stream().map(TaskDto::from).toList();
        return new TaskListResponse(items, items.size());
    }

    @GetMapping("/{id}")
    public TaskResponse getTask(@PathVariable UUID id) {
        return new TaskResponse(TaskDto.from(taskService.getTask(id)));
    }

    @PostMapping
    public ResponseEntity<TaskResponse> createTask(@RequestBody @Valid CreateTaskRequest request) {
        return ResponseEntity.status(201)
                .body(new TaskResponse(TaskDto.from(taskService.createTask(request.title(), request.description()))));
    }

    @PatchMapping("/{id}/status")
    public TaskResponse updateTaskStatus(@PathVariable UUID id, @RequestBody @Valid UpdateTaskStatusRequest request) {
        return new TaskResponse(TaskDto.from(taskService.updateTaskStatus(id, request.status())));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable UUID id) {
        taskService.deleteTask(id);
        return ResponseEntity.noContent().build();
    }
}
