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
    @staticmethod
    def save_result(result: AnalysisResult):
        ANSWERS_DIR.mkdir(exist_ok=True, parents=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # analysis_id is now mandatory
        if not result.analysis_id or not result.analysis_id.strip():
            raise ValueError("analysis_id is required for artifact storage and cannot be empty.")
        base_name = result.analysis_id.strip().replace(" ", "_")

        filename = f"{base_name}.json"
        path = ANSWERS_DIR / filename

        payload = {
            "timestamp": result.timestamp,
            "query": result.query,
            "pdf_path": result.pdf_path,
            "followups": result.followups,
            "analysis_id": result.analysis_id,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
