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

        # output_name is now mandatory
        if not result.output_name or not result.output_name.strip():
            raise ValueError("output_name is required for artifact storage and cannot be empty.")
        base_name = result.output_name.strip().replace(" ", "_")[:64]

        filename = f"{ts}-{base_name}.json"
        path = ANSWERS_DIR / filename

        payload = {
            "timestamp": result.timestamp,
            "query": result.query,
            "pdf_path": result.pdf_path,
            "followups": result.followups,
            "output_name": result.output_name,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
