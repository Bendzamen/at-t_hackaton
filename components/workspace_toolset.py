from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.schema import Data
from langflow.io import Output
from langchain.tools import StructuredTool
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List
import pathlib
import subprocess
import shlex

ROOT = pathlib.Path("/app/workspace").resolve()
ALLOWED = {"ls", "cat", "git", "python", "pytest", "ruff", "node", "npm", "rg", "pip"}
WORKDIR = ROOT


def inside_root(p: pathlib.Path) -> bool:
    try:
        p.resolve().relative_to(ROOT)
        return True
    except Exception:
        return False


# Tool input schemas
class ReadFileInput(BaseModel):
    path: str = Field(description="Path to file relative to workspace")


class WriteFileInput(BaseModel):
    path: str = Field(description="Path to file relative to workspace")
    content: str = Field(description="Content to write to the file")


class ListDirInput(BaseModel):
    path: str = Field(default=".", description="Directory path relative to workspace")


class ShellInput(BaseModel):
    command: str = Field(description=f"Shell command. Allowed: {', '.join(sorted(ALLOWED))}")


# Tool functions
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


def write_file_func(path: str, content: str) -> str:
    """Write UTF-8 text to a file in the workspace (creates directories)."""
    p = (ROOT / path).resolve()
    if not inside_root(p):
        return "Error: Path escapes workspace"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Success: Wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error: {e}"


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


def shell_command_func(command: str) -> str:
    """Run approved shell commands in the sandboxed workspace."""
    try:
        exe = shlex.split(command)[0]
    except Exception:
        return "Error: Could not parse command"
    
    if exe not in ALLOWED:
        return f"Error: '{exe}' not allowed. Allowed: {', '.join(sorted(ALLOWED))}"
    
    try:
        proc = subprocess.run(
            command,
            cwd=str(WORKDIR),
            shell=True,
            capture_output=True,
            text=True,
            timeout=25,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(WORKDIR)}
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        if len(output) > 8000:
            output = output[:8000] + "\n[output truncated]"
        result = output if output.strip() else f"(no output)"
        return f"{result}\n[exit code: {proc.returncode}]"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 25s"
    except Exception as e:
        return f"Error: {e}"


class WorkspaceToolset(LCToolComponent):
    display_name = "Workspace Toolset"
    description = "Provides AI agents with file system and shell access tools"
    documentation = "https://python.langchain.com/docs/modules/tools/"

    outputs = [
        Output(name="tools", display_name="Tools", method="build_tools")
    ]

    def build_config(self):
        return {}

    def build_tools(self) -> List[BaseTool]:
        """Build and return all workspace tools as a list."""
        tools = [
            StructuredTool(
                name="read_file",
                description="Read a UTF-8 text file from the workspace. Use this to read existing code or data files. Input should be the file path relative to workspace root.",
                func=read_file_func,
                args_schema=ReadFileInput
            ),
            StructuredTool(
                name="write_file",
                description="Write UTF-8 text to a file in the workspace. Creates directories if needed. Use this to create new files or overwrite existing ones. Inputs: path (relative to workspace) and content (the text to write).",
                func=write_file_func,
                args_schema=WriteFileInput
            ),
            StructuredTool(
                name="list_directory",
                description="List files and directories in the workspace. Use this to explore the file structure. Input should be directory path relative to workspace (default: current directory).",
                func=list_directory_func,
                args_schema=ListDirInput
            ),
            StructuredTool(
                name="shell_command",
                description=f"Run shell commands in the workspace. Allowed commands: {', '.join(sorted(ALLOWED))}. Use this to run code, install packages, or execute tests. Input should be the shell command string.",
                func=shell_command_func,
                args_schema=ShellInput
            ),
        ]
        return tools
    
    def build(self, **kwargs) -> List[BaseTool]:
        """Alias for build_tools for backward compatibility."""
        return self.build_tools()
