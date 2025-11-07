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


class SafeReadFile(CustomComponent):
    display_name = "Read File"
    description = "Read a UTF-8 text file inside the workspace."

    def build_config(self):
        return {"path": {"display_name": "File Path", "value": "", "info": "Path relative to workspace"}}

    def build(self) -> Data:
        path = getattr(self, "path", "")
        p = (ROOT / path).resolve()
        if not inside_root(p):
            return Data(value="Error: Path escapes workspace")
        if not p.exists() or not p.is_file():
            return Data(value="Error: File not found")
        try:
            content = p.read_text(encoding="utf-8")
            return Data(value=content)
        except Exception as e:
            return Data(value=f"Error: {e}")


class SafeWriteFile(CustomComponent):
    display_name = "Write File"
    description = "Write UTF-8 text to a file inside the workspace (creates dirs)."

    def build_config(self):
        return {
            "path": {"display_name": "File Path", "value": "", "info": "Path relative to workspace"},
            "content": {"display_name": "Content", "multiline": True, "value": ""}
        }

    def build(self) -> Data:
        path = getattr(self, "path", "")
        content = getattr(self, "content", "")
        p = (ROOT / path).resolve()
        if not inside_root(p):
            return Data(value="Error: Path escapes workspace")
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return Data(value=f"Success: Wrote {len(content)} characters to {path}")
        except Exception as e:
            return Data(value=f"Error: {e}")


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
            listing = "\n".join(entries)
            return Data(value=listing)
        except Exception as e:
            return Data(value=f"Error: {e}")

