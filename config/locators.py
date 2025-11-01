import re

RE_DEEP_RESEARCH = re.compile(r"^Deep\s*Research$", re.I)
RE_START_RESEARCH = re.compile(r"\bStart\s*research\b", re.I)
RE_SHARE_EXPORT = re.compile(r"^\s*Share\s*&\s*Export\s*$", re.I)
RE_EXPORT_TO_DOCS = re.compile(r"Export\s+to\s+Docs", re.I)
RE_COMPLETED = re.compile(r"I[’']ve\s+completed\s+your\s+research\.?", re.I)
RE_FOLLOWUP_WAIT = re.compile(r"Just a sec\.\.\.", re.I)

CHAT_CONTAINER = ".chat-container"
RESPONSE_CONTAINER = "response-container"
MESSAGE_CONTENT = "message-content"
