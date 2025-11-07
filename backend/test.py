import os
import shutil
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, project

client = TestClient(app)

DATA_DIR = "data/project"

def setup_function():
    """ setup any state specific to the execution of the given function."""
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR)
    project.__init__()

def teardown_function():
    """ teardown any state that was previously setup with a setup_function
    function.
    """
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)

@patch('main.trigger_langflow_with_file')
def test_start_processing(mock_trigger_langflow):
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        response = client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    assert response.status_code == 200
    json_response = response.json()
    assert json_response == {"message": "Processing started"}
    
    assert os.path.isdir(project.project_dir)
    assert os.path.isfile(os.path.join(project.project_dir, "concept.pdf"))
    assert os.path.isfile(os.path.join(project.project_dir, "history.json"))
    code_dir = os.path.join(project.project_dir, "code")
    assert os.path.isdir(code_dir)
    assert os.path.isdir(os.path.join(code_dir, ".git"))

    mock_trigger_langflow.assert_called_once()
    assert f"Sent to langflow with code_dir: {project.code_dir}" in project.history

@patch('main.trigger_langflow_with_file')
def test_get_status(mock_trigger_langflow):
    # First create a project
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    # Now get the status
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    assert json_response[0] == "Initial PDF submission"

@patch('main.trigger_langflow_with_file')
def test_update_status(mock_trigger_langflow):
    # First create a project
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    # Update the status
    response = client.post("/update-status", json={"stage": "test_stage", "message": "test_message"})
    assert response.status_code == 200
    assert response.json() == {"message": "Status updated successfully"}

    # Check the status
    assert len(project.history) == 3
    iteration = project.history[-1]
    assert len(iteration.status_list) == 1
    status = iteration.status_list[0]
    assert status["stage"] == "test_stage"
    assert status["message"] == "test_message"