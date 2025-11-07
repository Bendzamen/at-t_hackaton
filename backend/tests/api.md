# API Endpoints

## POST /start

Initiates a new project from a PDF file.

- **Request:** `multipart/form-data` with a `file` field containing the PDF.
- **Response:** `{"message": "Processing started"}`

## GET /status

Retrieves the history of the project.

- **Response:** A JSON array representing the project's history.

## POST /update-status

Adds a status update to the project's latest iteration.

- **Request:** `{"stage": "<string>", "message": "<string>"}`
- **Response:** `{"message": "Status updated successfully"}`

## POST /iteration-done

Marks the current iteration as complete, commits the code, and provides a download link for the code.

- **Response:** `{"message": "Iteration marked as done"}`

## GET /zip-download

Downloads a zip file of the `code` folder.

- **Response:** A zip file of the `code` directory.

## POST /undo

Rolls back the last commit and removes the last iteration from the history.

- **Response:** `{"message": "Rolled back to the previous commit"}`
