from langflow.custom import Component
import pathlib

ROOT = pathlib.Path("/app/workspace").resolve()

def inside_root(p: pathlib.Path) -> bool:
    try:
        p.resolve().relative_to(ROOT)
        return True
    except Exception:
        return False

class SafeReadFile(Component):
    display_name = "Read File"
    description = "Read a UTF-8 text file inside the workspace."
    inputs = [{"name": "path", "type": "str", "required": True}]
    outputs = [{"name": "content", "type": "str"}]

    def run(self, path: str):
        p = (ROOT / path).resolve()
        if not inside_root(p):
            return "Rejected: path escapes workspace."
        if not p.exists() or not p.is_file():
            return "Error: file not found."
        try:
            return p.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error: {e}"

class SafeWriteFile(Component):
    display_name = "Write File"
    description = "Write UTF-8 text to a file inside the workspace (creates dirs)."
    inputs = [
        {"name": "path", "type": "str", "required": True},
        {"name": "content", "type": "str", "required": True},
    ]
    outputs = [{"name": "status", "type": "str"}]

    def run(self, path: str, content: str):
        p = (ROOT / path).resolve()
        if not inside_root(p):
            return "Rejected: path escapes workspace."
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return "ok"
        except Exception as e:
            return f"Error: {e}"

class ListDir(Component):
    display_name = "List Directory"
    description = "List files in a directory inside the workspace."
    inputs = [{"name": "path", "type": "str", "required": False}]
    outputs = [{"name": "listing", "type": "str"}]

    def run(self, path: str = "."):
        p = (ROOT / path).resolve()
        if not inside_root(p) or not p.exists() or not p.is_dir():
            return "Error: invalid directory."
        try:
            entries = []
            for child in sorted(p.iterdir()):
                kind = "DIR" if child.is_dir() else "FILE"
                entries.append(f"{kind}\t{child.name}")
            return "\n".join(entries)
        except Exception as e:
            return f"Error: {e}"
