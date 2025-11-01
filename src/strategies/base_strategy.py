from abc import ABC, abstractmethod
from src.automation.gemini_client import GeminiClient
from src.data.models import QueryRequest, AnalysisResult

class BaseStrategy(ABC):
    @abstractmethod
    def run(self, client: GeminiClient, request: QueryRequest) -> AnalysisResult: ...
