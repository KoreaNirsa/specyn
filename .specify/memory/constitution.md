# Spec Kit Constitution

## Source of Truth

Specifications are the source of truth. Implementation, tests, prompts, and generated artifacts must be derived from the active feature specification bundle.

## Feature-Based Specification Layout

All active feature specifications live under `specs/<number>-<feature-name>/`.

Each feature directory may contain:

- `spec.md`: product and requirement specification.
- `plan.md`: execution, agent, or implementation planning specification.
- `tasks.md`: validation and task-oriented specification.
- `api.md`: API and contract-facing specification.
- `review.md`: review and release quality specification.
- `contracts/`: OpenAPI or other machine-readable contracts.

## Migration Invariant

When migrating existing specifications into Spec Kit layout, the body and front matter of existing specification files must not be changed or deleted. Rename and move operations are allowed only to align files with the feature-based layout.

## Future Feature Slots

Future specifications should be added as independent feature directories instead of being mixed into existing feature bundles.

Reserved future feature areas:

- dashboard design specification.
- Grill Me review technique.
- TDD workflow and specification refinement policy.

## TDD Gate

All future implementation work must follow a TDD flow:

1. Define the failing test or validation command before implementation.
2. Confirm the failure or document why the failure cannot be executed.
3. Implement the smallest scoped change that satisfies the spec.
4. Re-run the same validation command and record the result.
5. Refactor only after the validation passes.

Work without TDD evidence must remain blocked unless the active spec explicitly records the reason and alternate validation method.
