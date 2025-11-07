import os
import json
import uuid
from typing import List, Dict, Union

DATA_DIR = "data/projects"

class Iteration:
    def __init__(self, commit_id: str = None):
        self.status_list: List[Dict] = []
        self.commit_id = commit_id

    def commit(self):
        if not self.commit_id:
            self.commit_id = str(uuid.uuid4())

    def to_dict(self):
        return {
            "status_list": self.status_list,
            "commit_id": self.commit_id
        }

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
            self.history: List[Union[str, Iteration]] = []
            os.makedirs(self.project_dir, exist_ok=True)

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
                self.history = []
                for item in history_data:
                    if isinstance(item, dict) and 'status_list' in item:
                        iteration = Iteration(commit_id=item.get('commit_id'))
                        iteration.status_list = item['status_list']
                        self.history.append(iteration)
                    else:
                        self.history.append(item)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            history_data = []
            for item in self.history:
                if isinstance(item, Iteration):
                    history_data.append(item.to_dict())
                else:
                    history_data.append(item)
            json.dump(history_data, f, indent=4)

    def add_prompt(self, prompt: str):
        self.history.append(prompt)
        self.save_history()

    def add_status(self, stage: str, message: str, zip_result: str = None, preview: str = None):
        if not self.history or not isinstance(self.history[-1], Iteration):
            self.history.append(Iteration())
        
        iteration = self.history[-1]
        status_index = len(iteration.status_list)
        status = {
            "stage": stage,
            "message": message,
            "zip_result": zip_result,
            "preview": preview,
            "index": status_index
        }
        iteration.status_list.append(status)
        self.save_history()