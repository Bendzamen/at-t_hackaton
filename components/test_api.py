import requests
import os
import uuid

# The complete API endpoint URL for your flow
url = "http://localhost:7860/api/v1/run/32ff08e2-e8b7-45bf-a7f9-a22a4589f077"

# It is recommended to store your API key as an environment variable
# for better security.
api_key = "sk-w8emllhYJLa-YAFg-u_vZyYvXMZmqWPy1Wnt07O7Q1s" 

headers = {
    "x-api-key": api_key 
}

# --- CORRECTED PAYLOAD ---
# The payload uses the 'tweaks' parameter to target the specific input
# field ('path') of the specific component ('File-YOUR_ID_HERE').
payload = {
    "input_value": "", # This can be an empty string if the flow starts with the file
    "output_type": "text",
    "session_id": str(uuid.uuid4()),
    "tweaks": {
        # 1. Replace "File-YOUR_ID_HERE" with the actual ID of your File node
        #    (Find it in the 'Advanced' tab of the component in the UI)
        "File-setGR": {
            # 2. The input field is named "path"
            "path": [
                # 3. The value must be the path INSIDE the Docker container
                "/app/uploads/requirements.pdf"
            ]
        }
    }
}

try:
    # Send API request with the corrected payload
    print("Sending payload to Langflow:", payload)
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise exception for bad status codes

    # Print the successful response
    print("\n--- Response from server ---")
    print(response.json())

except requests.exceptions.RequestException as e:
    print(f"\n--- Error making API request ---")
    print(f"Error: {e}")
    # This is helpful for debugging API errors
    if e.response:
        print(f"Status Code: {e.response.status_code}")
        print(f"Response Body: {e.response.text}")
except ValueError as e:
    print(f"Error parsing response: {e}")