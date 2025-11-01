from pathlib import Path
from typing import Tuple, List, Dict, Optional
from config.settings import QUERY_DELIMITER, FOLLOWUP_DELIMITER, DEFAULT_FOLLOWUP_BLOCK

def read_queries_file(path: str = "queries.txt") -> Tuple[Optional[list], List[Dict[str, list]]]:
    text = Path(path).read_text(encoding="utf-8").lstrip()
    defaults = None
    segments_part = text
    if text.startswith(DEFAULT_FOLLOWUP_BLOCK):
        parts = text.split(DEFAULT_FOLLOWUP_BLOCK, 1)[1]
        first_split = parts.split(QUERY_DELIMITER, 1)
        defaults_block = first_split[0]
        segments_part = first_split[1] if len(first_split) > 1 else ""
        defaults = [chunk.strip() for chunk in defaults_block.strip().split(FOLLOWUP_DELIMITER) if chunk.strip()]
    segments = [s.strip() for s in segments_part.split(QUERY_DELIMITER) if s.strip()]
    result = []
    for seg in segments:
        parts = [p.strip() for p in seg.split(FOLLOWUP_DELIMITER)]
        query = parts[0]
        followups = [p for p in parts[1:] if p]
        result.append({"query": query, "followups": followups})
    return defaults, result
