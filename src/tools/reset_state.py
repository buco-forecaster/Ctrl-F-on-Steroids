from pathlib import Path
import shutil
from config.settings import AUTH_STATE_PATH, CHROME_PROFILE_DIR, OUTPUTS_DIR
import sys

def _rm(target: Path, label: str):
    print(f"RESET: {label}: {target} exists_before={target.exists()}")
    if target.exists():
        try:
            if target.is_file():
                target.unlink()
            else:
                shutil.rmtree(target, ignore_errors=True)
        except Exception as e:
            print(f"Failed to delete {target}: {e}")
    print(f"RESET: {label}: {target} exists_after={target.exists()}")

def reset_full():
    # Compute project root from this file's parent chain
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]
    print(f"RESET: Current working directory: {Path.cwd()}")
    print(f"RESET: Project root according to script: {project_root}")

    auth_dir = (project_root / AUTH_STATE_PATH).resolve().parent
    outputs_dir = (project_root / OUTPUTS_DIR).resolve()
    chrome_profile_dir = CHROME_PROFILE_DIR.expanduser().resolve()

    _rm(auth_dir, ".auth")
    _rm(chrome_profile_dir, "chrome-automation-profile")
    _rm(outputs_dir, "outputs")

    print("RESET: Full reset DONE (_rm printed per-target existence before/after)")

if __name__ == "__main__":
    reset_full()
