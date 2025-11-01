from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class QueryRequest:
    query: str
    followups: List[str]

@dataclass
class AnalysisResult:
    timestamp: str
    query: str
    followups: Dict[str, str]
    pdf_path: Optional[str] = None
