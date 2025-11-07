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


class ListDirInput(BaseModel):
    path: str = Field(default=".", description="Directory path relative to workspace")


def list_directory_func(path: str = ".") -> str:
    """List files and directories in the workspace."""
    p = (ROOT / path).resolve()
    if not inside_root(p):
        return "Error: Path escapes workspace"
    if not p.exists() or not p.is_dir():
        return "Error: Invalid directory"
    try:
        entries = []
        for child in sorted(p.iterdir()):
            kind = "DIR" if child.is_dir() else "FILE"
            size = ""
            if child.is_file():
                try:
                    size = f" ({child.stat().st_size} bytes)"
                except:
                    pass
            entries.append(f"{kind}\t{child.name}{size}")
        return "\n".join(entries) if entries else "(empty directory)"
    except Exception as e:
        return f"Error: {e}"


class ListDirectoryTool(LCToolComponent):
    display_name = "List Directory Tool"
    description = "Tool to list directory contents in workspace"
    name = "ListDirectoryTool"
    
    outputs = [Output(name="list_directory_tool", display_name="Tool", method="build_list_directory_tool")]
    
    def build_config(self):
        return {}
    
    def build_list_directory_tool(self) -> StructuredTool:
        return StructuredTool(
            name="list_directory",
            description="List files and directories in the workspace. Use this to explore the file structure. Input should be directory path relative to workspace (default: current directory '.').",
            func=list_directory_func,
            args_schema=ListDirInput
        )
