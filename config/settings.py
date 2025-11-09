from pathlib import Path

# Core configuration
GEMINI_URL = "https://gemini.google.com/app"
GOOGLE_ACCOUNTS_URL = "https://accounts.google.com/"
AUTH_STATE_PATH = Path(".auth/storage_state_chrome.json")
CHROME_PROFILE_DIR = Path.home() / "chrome-automation-profile"

# Browser environment
VIEWPORT = {"width": 1900, "height": 1280}
LOCALE = "en-US"
TIMEZONE_ID = "Europe/Prague"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0.0.0 Safari/537.36")

# Timeouts (ms)
DEFAULT_TIMEOUT_MS = 60_000
DEFAULT_START_RESEARCH_TIMEOUT_MS = 120_000
DEFAULT_DEEP_RESEARCH_TIMEOUT_MS = 15 * 60_000
# Output paths
OUTPUTS_DIR = Path("outputs")
ANSWERS_DIR = OUTPUTS_DIR / "answers"

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "gemini"
STOCKS_COLLECTION = "stock_results"
SOCCER_COLLECTION = "soccer_results"
MONGO_CONN_TIMEOUT_MS = 5000
MONGO_SOCKET_TIMEOUT_MS = 5000

# New template and variable mode delimiters
VARIABLES_SEPARATOR = '---VARIABLES_SEPARATOR---'
CONTENT_TEMPLATE_BEGIN = '---CONTENT_TEMPLATE---'
CONTENT_TEMPLATE_END = '---END_CONTENT_TEMPLATE---'
CONTENT_SEPARATOR = '---CONTENT_SEPARATOR---'

# Delimiters
QUERY_DELIMITER = '---QUERY_SEPARATOR---'
FOLLOWUP_DELIMITER = '---FOLLOWUP_SEPARATOR---'
DEFAULT_FOLLOWUP_BLOCK = '---DEFAULT-FOLLOWUP---'
