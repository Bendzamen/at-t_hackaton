from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.encoders import jsonable_encoder
import os
from project import Project
from pydantic import BaseModel
from langflow_client import trigger_langflow_with_file
import shutil
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

project = Project()

@app.post("/start")
async def start_processing(file: UploadFile = File(...)):
    file_path = os.path.join(project.project_dir, "concept.pdf")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    project.add_prompt("Initial PDF submission")
    
    # Trigger Langflow
    trigger_langflow_with_file(file_path, project.code_dir)

    return {"message": "Processing started"}

@app.get("/status")
async def get_status():
    history = []
    for item in project.history:
        if isinstance(item, str):
            if item == f"Sent to langflow with code_dir: {project.code_dir}":
                continue
            history.append(item)
        else:
            history.append(item.status_list)
    return jsonable_encoder(history)

class UpdateStatusRequest(BaseModel):
    stage: str
    message: str

@app.post("/update-status")
async def update_status(request: UpdateStatusRequest):
    project.add_status(stage=request.stage, message=request.message)
    return {"message": "Status updated successfully"}

@app.post("/iteration-done")
async def iteration_done():
    project.add_status(stage="Finished", message="Iteration complete", zip_result="/zip-download")
    project.history[-1].commit()
    return {"message": "Iteration marked as done"}

@app.get("/zip-download")
async def zip_download():
    shutil.make_archive("code", 'zip', project.code_dir)
    return FileResponse("code.zip", media_type='application/zip', filename='code.zip')

@app.post("/undo")
async def undo():
    project.rollback()
    return {"message": "Rolled back to the previous commit"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)