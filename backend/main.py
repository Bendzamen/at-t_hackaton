from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
import os
from project import Project
from pydantic import BaseModel
from langflow_client import trigger_langflow_with_file

app = FastAPI()

project = Project()

@app.post("/start")
async def start_processing(file: UploadFile = File(...)):
    file_path = os.path.join(project.project_dir, "concept.pdf")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    project.add_prompt("Initial PDF submission")
    
    # Trigger Langflow
    trigger_langflow_with_file(file_path, project.code_dir)
    project.add_prompt(f"Sent to langflow with code_dir: {project.code_dir}")

    return {"message": "Processing started"}

@app.get("/status")
async def get_status():
    return jsonable_encoder(project.history)

class UpdateStatusRequest(BaseModel):
    stage: str
    message: str

@app.post("/update-status")
async def update_status(request: UpdateStatusRequest):
    project.add_status(stage=request.stage, message=request.message)
    return {"message": "Status updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)