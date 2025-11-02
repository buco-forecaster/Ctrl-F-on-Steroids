from datetime import datetime
from src.automation.gemini_client import GeminiClient
from src.data.models import QueryRequest, AnalysisResult

class StockStrategy:
    def run(self, client: GeminiClient, request: QueryRequest) -> AnalysisResult:
        pdf_path = client.execute_deep_research(request.query, output_name=request.output_name)
        followups = client.ask_followups(request.followups)
        client.new_chat()

        return AnalysisResult(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            query=request.query,
            followups=followups,
            pdf_path=pdf_path,
            output_name=request.output_name,
        )
