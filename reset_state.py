from pathlib import Path
import shutil
from config.settings import AUTH_STATE_PATH, CHROME_PROFILE_DIR, OUTPUTS_DIR

def _rm(target: Path):
    if target.exists():
        if target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target, ignore_errors=True)

def reset_full():
    _rm(AUTH_STATE_PATH.parent)  # removes .auth/ and storage_state
    _rm(CHROME_PROFILE_DIR)      # removes Chrome persistent profile
    _rm(OUTPUTS_DIR)             # removes outputs/
    print("Full reset: .auth, Chrome profile, and outputs/ were removed.")

if __name__ == "__main__":
    reset_full()
