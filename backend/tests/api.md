# API Endpoints

## GET /projects

Lists all project IDs.

## POST /start

Initiates a new project from a PDF file.

- **Request:** `multipart/form-data` with a `file` field containing the PDF.
- **Response:** `{"project_id": "<uuid>"}`

## POST /status

Retrieves the history of a project.

- **Request:** `{"project_id": "<uuid>"}`
- **Response:** A JSON array representing the project's history.

## POST /update-status

Adds a status update to a project's latest iteration.

- **Request:** `{"project_id": "<uuid>", "stage": "<string>", "message": "<string>"}`
- **Response:** `{"message": "Status updated successfully"}`
