from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class QueryRequest:
    query: str
    followups: Dict[str, str]
    analysis_id: str  # Now required

@dataclass
class AnalysisResult:
    timestamp: str
    query: str
    followups: Dict[str, str]
    pdf_path: str  # Now required
    analysis_id: str  # Now required
    result: dict
