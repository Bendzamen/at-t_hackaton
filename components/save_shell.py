from langflow.custom import Component
import subprocess, shlex, pathlib, os

# Allow-list only what you really need
ALLOWED = {"ls", "cat", "git", "python", "pytest", "ruff", "node", "npm", "rg"}
WORKDIR = pathlib.Path("/app/workspace").resolve()

class SafeShell(Component):
    display_name = "Safe Shell"
    description = "Run approved shell commands in the sandboxed workspace."
    inputs = [{"name": "command", "type": "str", "required": True, "display_name": "Command"}]
    outputs = [{"name": "result", "type": "str"}]

    def run(self, command: str):
        # basic parsing of the binary being requested
        try:
            exe = shlex.split(command)[0]
        except Exception:
            return "Rejected: could not parse command."

        if exe not in ALLOWED:
            return f"Rejected: '{exe}' is not in allow-list."

        try:
            proc = subprocess.run(
                command,
                cwd=str(WORKDIR),
                shell=True,
                capture_output=True,
                text=True,
                timeout=25,
                env={}  # empty env for safety; add whitelisted vars if needed
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            # Trim overly long output to avoid overwhelming the LLM
            if len(output) > 8000:
                output = output[:8000] + "\n[truncated]"
            return output
        except subprocess.TimeoutExpired:
            return "Command timed out after 25s."
        except Exception as e:
            return f"Error: {e}"
