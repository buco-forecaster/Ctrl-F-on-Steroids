from datetime import datetime
from linecache import clearcache

from config.settings import DEFAULT_TIMEOUT_MS
from src.automation.gemini_client import GeminiClient
from src.data.models import QueryRequest, AnalysisResult
from src.data.mongo_repository import StockMongoRepository

class StockStrategy:
    def run(self, client: GeminiClient, request: QueryRequest) -> AnalysisResult:
        max_attempts = 3

        attempts = 0
        while attempts < max_attempts:
            try:
                pdf_path = client.execute_deep_research(request.query, analysis_id=request.analysis_id)
                break
            except Exception as e:
                print(f"Error during deep research execution: {e}")
                client.new_chat()

            attempts += 1

        if attempts == max_attempts:
            raise RuntimeError("Failed to execute deep research after multiple attempts.")

        attempts = 0
        while attempts < max_attempts:
            try:
                followups = client.ask_followups(request.followups)
                break
            except Exception as e:
                print(f"Error during deep research execution: {e}")
                client.page.reload(timeout=DEFAULT_TIMEOUT_MS)

            attempts += 1

        if attempts == max_attempts:
            raise RuntimeError("Failed to ask follow-up questions after multiple attempts.")

        client.new_chat()

        result = AnalysisResult(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            query=request.query,
            followups=followups,  # {key: answer}
            pdf_path=pdf_path,
            analysis_id=request.analysis_id,
        )

        # Store result also in MongoDB (stock_results collection)
        StockMongoRepository().save_result(result)
        return result
