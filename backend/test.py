import os
import shutil
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, project
import zipfile

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
    if os.path.exists("code.zip"):
        os.remove("code.zip")

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
    assert "Initial PDF submission" in project.history

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
    assert len(json_response) == 1
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
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    assert json_response[0] == "Initial PDF submission"
    status_list = json_response[1]
    assert len(status_list) == 1
    status = status_list[0]
    assert status["stage"] == "test_stage"
    assert status["message"] == "test_message"

@patch('main.trigger_langflow_with_file')
def test_iteration_done(mock_trigger_langflow):
    # First create a project
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    # Mark iteration as done
    response = client.post("/iteration-done")
    assert response.status_code == 200
    assert response.json() == {"message": "Iteration marked as done"}

    # Check the status
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    status_list = json_response[1]
    assert len(status_list) == 1
    status = status_list[0]
    assert status["stage"] == "Finished"
    assert status["message"] == "Iteration complete"
    assert status["zip_result"] == "/zip-download"

@patch('main.trigger_langflow_with_file')
def test_zip_download(mock_trigger_langflow):
    # First create a project
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    # Create a file in the code directory
    with open(os.path.join(project.code_dir, "test.txt"), "w") as f:
        f.write("test content")

    # Download the zip
    response = client.get("/zip-download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    # Check the zip content
    with open("code.zip", "wb") as f:
        f.write(response.content)
    
    with zipfile.ZipFile("code.zip", 'r') as zip_ref:
        assert "test.txt" in zip_ref.namelist()

@patch('main.trigger_langflow_with_file')
def test_undo(mock_trigger_langflow):
    # First create a project
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    # Mark iteration as done
    client.post("/iteration-done")

    # Undo the last commit
    response = client.post("/undo")
    assert response.status_code == 200
    assert response.json() == {"message": "Rolled back to the previous commit"}

    # Check the status
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0] == "Initial PDF submission"