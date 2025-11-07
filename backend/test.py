
import os
import shutil
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

DATA_DIR = "data/projects"

def setup_function():
    """ setup any state specific to the execution of the given function."""
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR)

def teardown_function():
    """ teardown any state that was previously setup with a setup_function
    function.
    """
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)

def test_start_processing():
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        response = client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")

    assert response.status_code == 200
    json_response = response.json()
    assert "project_id" in json_response
    project_id = json_response["project_id"]
    
    project_dir = os.path.join(DATA_DIR, project_id)
    assert os.path.isdir(project_dir)
    assert os.path.isfile(os.path.join(project_dir, "concept.pdf"))
    assert os.path.isfile(os.path.join(project_dir, "history.json"))

def test_get_status_not_found():
    response = client.post("/status", json={"project_id": "non-existent-id"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

def test_get_status_found():
    # First create a project
    with open("test.pdf", "wb") as f:
        f.write(b"This is a test pdf.")
    
    with open("test.pdf", "rb") as f:
        response = client.post("/start", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove("test.pdf")
    project_id = response.json()["project_id"]

    # Now get the status
    response = client.post("/status", json={"project_id": project_id})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["project_id"] == project_id
    assert "history" in json_response
    assert len(json_response["history"]) == 1
    assert json_response["history"][0] == "Initial PDF submission"
