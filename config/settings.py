from pathlib import Path
from unittest.mock import DEFAULT

# Core configuration
GEMINI_URL = "https://gemini.google.com/app"
GOOGLE_ACCOUNTS_URL = "https://accounts.google.com/"
AUTH_STATE_PATH = Path(".auth/storage_state_chrome.json")
CHROME_PROFILE_DIR = Path.home() / "chrome-automation-profile"

# Browser environment
VIEWPORT = {"width": 2120, "height": 1080}
LOCALE = "en-US"
TIMEZONE_ID = "Europe/Prague"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0.0.0 Safari/537.36")

# Timeouts (ms)
DEFAULT_TIMEOUT_MS = 60_000
DEFAULT_START_RESEARCH_TIMEOUT_MS = 120_000
DEFAULT_DEEP_RESEARCH_TIMEOUT_MS = 10 * 60_000
# Output paths
OUTPUTS_DIR = Path("outputs")
ANSWERS_DIR = OUTPUTS_DIR / "answers"

# New template and variable mode delimiters
VARIABLES_SEPARATOR = '---VARIABLES_SEPARATOR---'
CONTENT_TEMPLATE_BEGIN = '---CONTENT_TEMPLATE---'
CONTENT_TEMPLATE_END = '---END_CONTENT_TEMPLATE---'
CONTENT_SEPARATOR = '---CONTENT_SEPARATOR---'

# Delimiters
QUERY_DELIMITER = '---QUERY_SEPARATOR---'
FOLLOWUP_DELIMITER = '---FOLLOWUP_SEPARATOR---'
DEFAULT_FOLLOWUP_BLOCK = '---DEFAULT-FOLLOWUP---'
