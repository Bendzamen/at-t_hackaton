
from fastapi import FastAPI, File, UploadFile
import uuid
import os

app = FastAPI()

DATA_DIR = "data/projects"
os.makedirs(DATA_DIR, exist_ok=True)


@app.post("/start")
async def start_processing(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(DATA_DIR, f"{file_id}.pdf")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    return {"file_id": file_id, "file_path": file_path}

@app.get("/status")
async def get_status():
    return {
        "stage": "example stage",
        "message": "lorem ipsum",
        "i": 0
    }





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)
