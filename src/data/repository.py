from abc import ABC, abstractmethod
from .models import AnalysisResult

class Repository(ABC):
    @abstractmethod
    def save_result(self, result: AnalysisResult) -> str: ...
    # Optional: override for dynamic collection routing
    def save_result_to(self, collection: str, result: AnalysisResult) -> str:
        """
        Optionally implemented by repositories that support routing to a custom collection/table/etc.
        Default: fallback to save_result (ignores collection).
        """
        return self.save_result(result)
