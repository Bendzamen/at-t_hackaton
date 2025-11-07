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
