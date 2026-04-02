package com.sample.service.global.exception;

import com.sample.service.global.error.ErrorCode;
import com.sample.service.global.error.ErrorResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(TaskNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleTaskNotFound(TaskNotFoundException ex, HttpServletRequest request) {
        return build(HttpStatus.NOT_FOUND, ErrorCode.TASK_NOT_FOUND, ex.getMessage(), request);
    }

    @ExceptionHandler({
            MethodArgumentNotValidException.class,
            ConstraintViolationException.class,
            MethodArgumentTypeMismatchException.class,
            HttpMessageNotReadableException.class,
            InputValidationException.class
    })
    public ResponseEntity<ErrorResponse> handleValidation(Exception ex, HttpServletRequest request) {
        String message = resolveValidationMessage(ex);
        return build(HttpStatus.BAD_REQUEST, ErrorCode.VALIDATION_ERROR, message, request);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnhandled(Exception ex, HttpServletRequest request) {
        return build(HttpStatus.INTERNAL_SERVER_ERROR, ErrorCode.INTERNAL_SERVER_ERROR,
                "Unexpected server error", request);
    }

    private String resolveValidationMessage(Exception ex) {
        if (ex instanceof MethodArgumentNotValidException manv) {
            FieldError fieldError = manv.getBindingResult().getFieldError();
            if (fieldError != null) {
                return fieldError.getField() + " " + fieldError.getDefaultMessage();
            }
        }
        if (ex instanceof ConstraintViolationException cve && !cve.getConstraintViolations().isEmpty()) {
            return cve.getConstraintViolations().iterator().next().getMessage();
        }
        if (ex instanceof MethodArgumentTypeMismatchException matme) {
            return matme.getName() + " must be a valid " + matme.getRequiredType().getSimpleName();
        }
        if (ex instanceof HttpMessageNotReadableException) {
            return "Request body is invalid";
        }
        return ex.getMessage() != null ? ex.getMessage() : "Validation failed";
    }

    private ResponseEntity<ErrorResponse> build(
            HttpStatus status,
            ErrorCode code,
            String message,
            HttpServletRequest request
    ) {
        return ResponseEntity.status(status)
                .body(ErrorResponse.of(code, message, request.getRequestURI()));
    }
}
