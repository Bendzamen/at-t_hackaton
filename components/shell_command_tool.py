from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.io import Output
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import pathlib
import subprocess
import shlex
import os

# Get allowed commands from environment or use defaults
ALLOWED = set(os.getenv('ALLOWED_SHELL_COMMANDS', 'ls,cat,git,python,pytest,ruff,node,npm,rg,pip,echo,mkdir,rm,cp,mv').split(','))
WORKDIR = pathlib.Path("/app/workspace").resolve()


class ShellInput(BaseModel):
    command: str = Field(description=f"Shell command. Allowed: {', '.join(sorted(ALLOWED))}")


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


class ShellCommandTool(LCToolComponent):
    display_name = "Shell Command Tool"
    description = "Tool to run shell commands in workspace"
    name = "ShellCommandTool"
    
    outputs = [Output(name="shell_command_tool", display_name="Tool", method="build_shell_command_tool")]
    
    def build_config(self):
        return {}
    
    def build_shell_command_tool(self) -> StructuredTool:
        return StructuredTool(
            name="shell_command",
            description=f"Run shell commands in the workspace. Allowed commands: {', '.join(sorted(ALLOWED))}. Use this to run code, install packages, or execute tests. Input should be the shell command string.",
            func=shell_command_func,
            args_schema=ShellInput
        )
