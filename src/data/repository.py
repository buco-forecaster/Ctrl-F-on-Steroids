from abc import ABC, abstractmethod
from .models import AnalysisResult

class Repository(ABC):
    @abstractmethod
    def save_result(self, result: AnalysisResult) -> str: ...
