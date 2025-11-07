from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.io import Output
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import pathlib

ROOT = pathlib.Path("/app/workspace").resolve()


def inside_root(p: pathlib.Path) -> bool:
    try:
        p.resolve().relative_to(ROOT)
        return True
    except Exception:
        return False


class WriteFileInput(BaseModel):
    path: str = Field(description="Path to file relative to workspace")
    content: str = Field(description="Content to write to the file")


def write_file_func(path: str, content: str) -> str:
    """Write UTF-8 text to a file in the workspace."""
    p = (ROOT / path).resolve()
    if not inside_root(p):
        return "Error: Path escapes workspace"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Success: Wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error: {e}"


class WriteFileTool(LCToolComponent):
    display_name = "Write File Tool"
    description = "Tool to write files to workspace"
    name = "WriteFileTool"
    
    outputs = [Output(name="write_file_tool", display_name="Tool", method="build_write_file_tool")]
    
    def build_config(self):
        return {}
    
    def build_write_file_tool(self) -> StructuredTool:
        return StructuredTool(
            name="write_file",
            description="Write UTF-8 text to a file in the workspace. Creates directories if needed. Inputs: path (relative to workspace) and content (the text to write).",
            func=write_file_func,
            args_schema=WriteFileInput
        )
