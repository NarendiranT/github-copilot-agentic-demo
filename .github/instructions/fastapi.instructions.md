---
applyTo: 'app/**/*.py'
---
# FastAPI Instructions

- Keep routers thin; separate business logic and persistence from HTTP handling.
- Use Pydantic request and response models, explicit status codes and FastAPI dependency injection.
- Validate at API boundaries; keep internal errors and sensitive fields out of responses.
- Use async endpoints for asynchronous I/O; avoid blocking calls in async functions.
- Preserve API contracts and maintain OpenAPI documentation through route metadata and schemas.