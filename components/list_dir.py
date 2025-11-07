from langflow.custom import CustomComponent
from langflow.schema import Data
import pathlib

ROOT = pathlib.Path("/app/workspace").resolve()


def inside_root(p: pathlib.Path) -> bool:
    try:
        p.resolve().relative_to(ROOT)
        return True
    except Exception:
        return False


class ListDir(CustomComponent):
    display_name = "List Directory"
    description = "List files in a directory inside the workspace."

    def build_config(self):
        return {"path": {"display_name": "Directory Path", "value": ".", "info": "Path relative to workspace"}}

    def build(self) -> Data:
        path = getattr(self, "path", ".")
        p = (ROOT / path).resolve()
        if not inside_root(p) or not p.exists() or not p.is_dir():
            return Data(value="Error: invalid directory.")
        try:
            entries = []
            for child in sorted(p.iterdir()):
                kind = "DIR" if child.is_dir() else "FILE"
                entries.append(f"{kind}\t{child.name}")
            listing = "\n".join(entries) if entries else "(empty directory)"
            return Data(value=listing)
        except Exception as e:
            return Data(value=f"Error: {e}")
