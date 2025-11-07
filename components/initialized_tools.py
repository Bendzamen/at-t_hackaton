"""Initialized tools - returns all tools as a list."""

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.io import Output
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import subprocess
import os
from pathlib import Path

WORKSPACE_ROOT = Path("/app/workspace")

def inside_root(p: Path) -> bool:
    """Check path traversal."""
    try:
        return p.resolve().is_relative_to(WORKSPACE_ROOT.resolve())
    except:
        return False

# Input schemas
class ReadFileInput(BaseModel):
    path: str = Field(description="File path relative to workspace")

class WriteFileInput(BaseModel):
    path: str = Field(description="File path relative to workspace")
    content: str = Field(description="Content to write to the file")

class ListDirInput(BaseModel):
    path: str = Field(default=".", description="Directory path relative to workspace (default: current directory)")

class ShellCommandInput(BaseModel):
    command: str = Field(description="Shell command to execute (allowed: ls, cat, git, python, pytest, ruff, node, npm, rg, pip)")

# Tool functions
def read_file_func(path: str) -> str:
    try:
        full_path = (WORKSPACE_ROOT / path).resolve()
        if not inside_root(full_path):
            return f"Error: Path outside workspace: {path}"
        if not full_path.exists():
            return f"Error: File not found: {path}"
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File: {path}\n\n{content}"
    except Exception as e:
        return f"Error reading {path}: {str(e)}"

def write_file_func(path: str, content: str) -> str:
    try:
        full_path = (WORKSPACE_ROOT / path).resolve()
        if not inside_root(full_path):
            return f"Error: Path outside workspace: {path}"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing {path}: {str(e)}"

def list_directory_func(path: str = ".") -> str:
    try:
        full_path = (WORKSPACE_ROOT / path).resolve()
        if not inside_root(full_path):
            return f"Error: Path outside workspace: {path}"
        if not full_path.exists():
            return f"Error: Directory not found: {path}"
        if not full_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        items = []
        for item in sorted(full_path.iterdir()):
            rel_path = item.relative_to(WORKSPACE_ROOT)
            if item.is_dir():
                items.append(f"[DIR]  {rel_path}/")
            else:
                size = item.stat().st_size
                items.append(f"[FILE] {rel_path} ({size} bytes)")
        
        return f"Contents of {path}:\n" + "\n".join(items) if items else f"Empty directory: {path}"
    except Exception as e:
        return f"Error listing {path}: {str(e)}"

# Get allowed commands from environment or use defaults
ALLOWED_COMMANDS = os.getenv('ALLOWED_SHELL_COMMANDS', 'ls,cat,git,python,pytest,ruff,node,npm,rg,pip').split(',')

def shell_command_func(command: str) -> str:
    cmd_parts = command.strip().split()
    if not cmd_parts or cmd_parts[0] not in ALLOWED_COMMANDS:
        return f"Error: Command not allowed. Allowed: {', '.join(ALLOWED_COMMANDS)}"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=25
        )
        output = result.stdout + result.stderr
        if len(output) > 8000:
            output = output[:8000] + "\n... (truncated)"
        return f"Command: {command}\nExit code: {result.returncode}\n\n{output}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 25s: {command}"
    except Exception as e:
        return f"Error executing {command}: {str(e)}"


class WorkspaceTools(LCToolComponent):
    display_name = "Workspace Tools (All)"
    description = "Returns all workspace tools: read_file, write_file, list_directory, shell_command"
    name = "WorkspaceToolsAll"
    
    outputs = [
        Output(name="tools_list", display_name="All Tools", method="build_all_tools")
    ]
    
    def build_config(self):
        return {}
    
    def build_all_tools(self) -> list[Tool]:
        """Return all 4 tools as a list."""
        
        read_tool = StructuredTool(
            name="read_file",
            description="Read a UTF-8 text file from the workspace. Use this to read existing code or data files. Input should be the file path relative to workspace root.",
            func=read_file_func,
            args_schema=ReadFileInput
        )
        
        write_tool = StructuredTool(
            name="write_file",
            description="Write UTF-8 text to a file in the workspace. Creates directories if needed. Use this to create new files or overwrite existing ones. Inputs: path (relative to workspace) and content (the text to write).",
            func=write_file_func,
            args_schema=WriteFileInput
        )
        
        list_tool = StructuredTool(
            name="list_directory",
            description="List files and directories in the workspace. Use this to explore the file structure. Input should be directory path relative to workspace (default: current directory).",
            func=list_directory_func,
            args_schema=ListDirInput
        )
        
        shell_tool = StructuredTool(
            name="shell_command",
            description=f"Run shell commands in the workspace. Allowed commands: {', '.join(ALLOWED_COMMANDS)}. Use this to run code, install packages, or execute tests. Input should be the shell command string.",
            func=shell_command_func,
            args_schema=ShellCommandInput
        )
        
        return [read_tool, write_tool, list_tool, shell_tool]
