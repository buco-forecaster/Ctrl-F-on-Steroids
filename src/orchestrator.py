from typing import List, Optional
from pathlib import Path
from playwright.sync_api import sync_playwright
from config.settings import AUTH_STATE_PATH
from src.automation.browser_manager import make_persistent_chrome
from src.automation.auth_handler import ensure_gemini_authenticated
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
            ctx = make_persistent_chrome(p)

            try:
                page = ensure_gemini_authenticated(ctx)
                # Ensure .auth folder exists before writing storage_state
                Path(AUTH_STATE_PATH).parent.mkdir(parents=True, exist_ok=True)
                ctx.storage_state(path=str(AUTH_STATE_PATH))
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
