package com.sample.service.domain.task.api;

import com.sample.service.domain.task.api.dto.CreateTaskRequest;
import com.sample.service.domain.task.api.dto.TaskListResponse;
import com.sample.service.domain.task.api.dto.TaskResponse;
import com.sample.service.domain.task.api.dto.UpdateTaskStatusRequest;
import com.sample.service.domain.task.application.TaskService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping
    public TaskListResponse getTasks() {
        return new TaskListResponse(
                taskService.getTasks().stream().map(TaskResponse::from).toList()
        );
    }

    @GetMapping("/{id}")
    public TaskResponse getTask(@PathVariable UUID id) {
        return TaskResponse.from(taskService.getTask(id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TaskResponse createTask(@Valid @RequestBody CreateTaskRequest request) {
        return TaskResponse.from(taskService.createTask(request.title()));
    }

    @PatchMapping("/{id}/status")
    public TaskResponse updateTaskStatus(@PathVariable UUID id, @Valid @RequestBody UpdateTaskStatusRequest request) {
        return TaskResponse.from(taskService.updateStatus(id, request.status()));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteTask(@PathVariable UUID id) {
        taskService.deleteTask(id);
    }
}
