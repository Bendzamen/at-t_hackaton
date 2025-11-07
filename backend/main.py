from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
import os
from project import Project
from pydantic import BaseModel

app = FastAPI()

DATA_DIR = "data/projects"
projects: dict[str, Project] = {}

def load_projects():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for project_id in os.listdir(DATA_DIR):
        if os.path.isdir(os.path.join(DATA_DIR, project_id)):
            project = Project(project_id=project_id)
            projects[project_id] = project

@app.on_event("startup")
async def startup_event():
    load_projects()

@app.post('/projects')
async def list_projects():
    return list(projects.keys())

@app.post("/start")
async def start_processing(file: UploadFile = File(...)):
    project = Project()
    projects[project.uuid] = project
    
    file_path = os.path.join(project.project_dir, "concept.pdf")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    project.add_prompt("Initial PDF submission")
    
    return {"project_id": project.uuid}

class StatusRequest(BaseModel):
    project_id: str

@app.post("/status")
async def get_status(request: StatusRequest):
    project = projects.get(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project_id": project.uuid, "history": jsonable_encoder(project.history)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)