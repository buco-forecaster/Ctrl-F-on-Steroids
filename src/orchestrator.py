import src.automation.auth_handler as auth_handler
import src.automation.browser_manager as browser_manager

from playwright.sync_api import sync_playwright
from src.automation.gemini_client import GeminiClient
from src.services.input_parser import read_queries_file
from src.data.models import QueryRequest
from src.data.repository import Repository

class Orchestrator:
    def __init__(self, strategy, repository: Repository):
        self.strategy = strategy
        self.repository = repository

    def run_batch(self, queries_file: str):
        with sync_playwright() as p:
            ctx = browser_manager.make_persistent_chrome(p)

            try:
                page = auth_handler.ensure_gemini_authenticated(ctx)
                auth_handler.store_auth_state(ctx)

                client = GeminiClient(page)
                defaults, segments = read_queries_file(queries_file)
                results = []

                for seg in segments:
                    followups = seg["followups"] or (defaults if defaults else {})

                    req = QueryRequest(query=seg["query"], followups=followups, analysis_id=seg["analysis_id"])
                    res = self.strategy.run(client, req)

                    collection = seg.get("collection")
                    # Prefer collection-aware save when available
                    if collection and hasattr(self.repository, "save_result_to"):
                        self.repository.save_result_to(collection, res)
                    else:
                        self.repository.save_result(res)
                    results.append(res)

                return results
            finally:
                ctx.close()
