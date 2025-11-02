from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class QueryRequest:
    query: str
    followups: List[str]
    output_name: str  # Now required

@dataclass
class AnalysisResult:
    timestamp: str
    query: str
    followups: Dict[str, str]
    pdf_path: str  # Now required
    output_name: str  # Now required
