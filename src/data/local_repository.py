import re
import json
from datetime import datetime
from pathlib import Path
from .models import AnalysisResult
from config.settings import ANSWERS_DIR

def _slug(s: str) -> str:
    import re
    return re.sub(r"[^a-zA-Z0-9_-]", "_", s)[:32]

class LocalRepository:
    def save_result(self, result: AnalysisResult) -> str:
        ANSWERS_DIR.mkdir(exist_ok=True, parents=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{ts}-{_slug(result.query)}.json"
        path = ANSWERS_DIR / fname
        payload = {
            "timestamp": result.timestamp,
            "query": result.query,
            "pdf_path": result.pdf_path,
            "followups": result.followups,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)
