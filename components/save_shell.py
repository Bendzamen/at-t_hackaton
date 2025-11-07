from langflow.custom import CustomComponent
from langflow.schema import Data
import subprocess, shlex, pathlib

# Allow-list only what you really need
ALLOWED = {"ls", "cat", "git", "python", "pytest", "ruff", "node", "npm", "rg", "pip"}
WORKDIR = pathlib.Path("/app/workspace").resolve()


class SafeShell(CustomComponent):
    display_name = "Safe Shell"
    description = "Run approved shell commands in the sandboxed workspace."

    def build_config(self):
        return {"command": {"display_name": "Command", "value": "", "info": f"Allowed: {', '.join(sorted(ALLOWED))}"}}

    def build(self) -> Data:
        command = getattr(self, "command", "")
        try:
            exe = shlex.split(command)[0]
        except Exception:
            return Data(value="Error: Could not parse command")

        if exe not in ALLOWED:
            return Data(value=f"Error: '{exe}' not allowed. Allowed: {', '.join(sorted(ALLOWED))}")

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
                output = output[:8000] + "\n[truncated]"
            result = output if output.strip() else f"(no output, exit code: {proc.returncode})"
            return Data(value=result)
        except subprocess.TimeoutExpired:
            return Data(value="Error: Command timed out after 25s")
        except Exception as e:
            return Data(value=f"Error: {e}")

