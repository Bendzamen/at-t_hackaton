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


class ReadFileInput(BaseModel):
    path: str = Field(description="Path to file relative to workspace")


def read_file_func(path: str) -> str:
    """Read a UTF-8 text file from the workspace."""
    p = (ROOT / path).resolve()
    if not inside_root(p):
        return "Error: Path escapes workspace"
    if not p.exists() or not p.is_file():
        return "Error: File not found"
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error: {e}"


class ReadFileTool(LCToolComponent):
    display_name = "Read File Tool"
    description = "Tool to read files from workspace"
    name = "ReadFileTool"
    
    outputs = [Output(name="read_file_tool", display_name="Tool", method="build_read_file_tool")]
    
    def build_config(self):
        return {}
    
    def build_read_file_tool(self) -> StructuredTool:
        return StructuredTool(
            name="read_file",
            description="Read a UTF-8 text file from the workspace. Input should be the file path relative to workspace root.",
            func=read_file_func,
            args_schema=ReadFileInput
        )
