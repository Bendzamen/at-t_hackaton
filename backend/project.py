
import os
import json
import uuid
from typing import List, Dict, Union

DATA_DIR = "data/projects"

class Project:
    def __init__(self, project_id: str = None):
        if project_id:
            self.uuid = project_id
            self.project_dir = os.path.join(DATA_DIR, self.uuid)
            self.history_file = os.path.join(self.project_dir, "history.json")
            self._load_history()
        else:
            self.uuid = str(uuid.uuid4())
            self.project_dir = os.path.join(DATA_DIR, self.uuid)
            self.history_file = os.path.join(self.project_dir, "history.json")
            self.history: List[Union[str, Dict]] = []
            os.makedirs(self.project_dir, exist_ok=True)

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def add_prompt(self, prompt: str):
        self.history.append(prompt)
        self.save_history()

    def add_status(self, stage: str, message: str, zip_result: str = None, preview: str = None):
        status_index = len([s for s in self.history if isinstance(s, dict)])
        status = {
            "stage": stage,
            "message": message,
            "zip_result": zip_result,
            "preview": preview,
            "index": status_index
        }
        self.history.append(status)
        self.save_history()
