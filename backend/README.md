test:
```
cd backend && ../backend/venv/bin/pytest test.py
```
+ REST test /tests

GUIDE FOR LANGCHAIN FLOW TRIGGER:

For many use cases, triggering the flow from your backend is the more common and simpler starting point. Here's how you can communicate *from* your Python backend *to* Langflow, including sending files like PDFs and additional text data.

The primary method for this is to make an HTTP POST request to Langflow's API endpoint for the specific flow you want to trigger.

### Triggering a Langflow Flow via API Request

To start a flow and send data to it, you'll interact with the `/api/v1/run/{flow_id}` endpoint. When sending files, the process is slightly different from sending just JSON data. You'll need to construct a `multipart/form-data` request.

Here’s a breakdown of the key steps and a Python example:

1.  **Identify Your Flow ID and API Endpoint:**
    *   The **Flow ID** is the unique identifier for your workflow, which you can find in the Langflow UI, often in the URL when you are editing the flow.
    *   The endpoint URL will be `http://<your_langflow_host>:<port>/api/v1/run/{flow_id}`.

2.  **Configure Your Langflow Flow to Accept Inputs:**
    *   Your flow needs a designated entry point for the data you're sending. This is typically done using input components like **"Chat Input"** or **"Text Input"**.
    *   When you send a request, you need to know the names of these input fields in your flow to map your data correctly. You can set these names in the component's settings within the Langflow UI.

3.  **Construct a `multipart/form-data` Request in Python:**
    *   The `requests` library in Python is perfect for this.
    *   You will send the file data (like your PDF) and any additional text data in the same request.

#### Python Example: Sending a PDF and Text Data to Langflow

Let's assume you have a Langflow flow with two input components:
*   A file input that will receive the PDF. Let's say you've configured it to expect a file.
*   A text input for additional instructions, which we'll call `"user_prompt"`.

First, make sure you have the `requests` library installed:
```bash
pip install requests
```

Here is the Python code for your backend:

```python
import requests
import os

# --- Configuration ---
LANGFLOW_API_URL = "http://127.0.0.1:7860"  # Replace with your Langflow instance URL
FLOW_ID = "YOUR_FLOW_ID"  # Replace with your specific Flow ID
# If you have set up an API key in Langflow, you'll need to include it.
# API_KEY = "YOUR_LANGFLOW_API_KEY"

# --- Data to Send ---
PDF_FILE_PATH = "path/to/your/document.pdf"
ADDITIONAL_TEXT_DATA = "Summarize the key findings in this document and list the authors."
# The name of the input field in your Langflow flow that expects the text data.
TEXT_INPUT_FIELD_NAME = "user_prompt"
# The name of the input field in your Langflow flow that expects the file.
FILE_INPUT_FIELD_NAME = "pdf_file"


def trigger_langflow_with_file(flow_id, file_path, text_data, text_field_name, file_field_name):
    """
    Triggers a Langflow flow, sending a file and additional text data.
    """
    endpoint = f"{LANGFLOW_API_URL}/api/v1/run/{flow_id}"

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        # Open the file in binary read mode
        with open(file_path, 'rb') as f:
            # Construct the multipart/form-data payload
            # The 'files' dictionary can also contain your text fields.
            files = {
                file_field_name: (os.path.basename(file_path), f, 'application/pdf'),
                text_field_name: (None, text_data)
            }

            # If you are using an API key, uncomment and set the headers
            # headers = {
            #     "x-api-key": API_KEY
            # }

            print("Sending request to Langflow...")
            # response = requests.post(endpoint, files=files, headers=headers)
            response = requests.post(endpoint, files=files) # Use this line if no API key

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with Langflow: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    result = trigger_langflow_with_file(
        FLOW_ID,
        PDF_FILE_PATH,
        ADDITIONAL_TEXT_DATA,
        TEXT_INPUT_FIELD_NAME,
        FILE_INPUT_FIELD_NAME
    )

    if result:
        print("Successfully triggered Langflow.")
        # The 'result' will contain the output of your flow's final component.
        # You might need to inspect the JSON to find the exact data you need.
        print("Response from Langflow:")
        print(result)

```

### How to Find the Input Field Names

1.  Go to your flow in the Langflow UI.
2.  Click on the input component (e.g., "Text Input").
3.  In the sidebar, look for the "Name" or "Field Name" parameter. This is the key you must use in your Python script (`TEXT_INPUT_FIELD_NAME` and `FILE_INPUT_FIELD_NAME` in the example).
4.  For file inputs, you will typically use a component that is designed to handle file uploads. The same principle of naming the input field applies.

By combining this approach with the custom component method from the previous answer, you can establish a robust, two-way communication channel:

1.  **Your Backend -> Langflow:** Trigger the flow and send the initial data (PDF, user prompts) using an HTTP POST request as shown above.
2.  **Langflow -> Your Backend:** During the flow's execution, use your custom "Progress Reporter" component to send status updates back to a dedicated endpoint on your backend.
