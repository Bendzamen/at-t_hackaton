
import requests
import os
from dotenv import load_dotenv

load_dotenv()

LANGFLOW_API_URL = os.getenv("LANGFLOW_API_URL")
FLOW_ID = os.getenv("FLOW_ID")
TEXT_INPUT_FIELD_NAME = os.getenv("TEXT_INPUT_FIELD_NAME")
FILE_INPUT_FIELD_NAME = os.getenv("FILE_INPUT_FIELD_NAME")

def trigger_langflow_with_file(file_path: str, text_data: str):
    """
    Triggers a Langflow flow, sending a file and additional text data.
    """
    endpoint = f"{LANGFLOW_API_URL}/api/v1/run/{FLOW_ID}"

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        with open(file_path, 'rb') as f:
            files = {
                FILE_INPUT_FIELD_NAME: (os.path.basename(file_path), f, 'application/pdf'),
                TEXT_INPUT_FIELD_NAME: (None, text_data)
            }

            print("Sending request to Langflow...")
            response = requests.post(endpoint, files=files)
            response.raise_for_status()

            return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with Langflow: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
