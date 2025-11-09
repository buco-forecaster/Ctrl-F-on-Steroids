from __future__ import annotations
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from config.settings import (
    MONGO_URI,
    MONGO_DB_NAME,
    STOCKS_COLLECTION,
    SOCCER_COLLECTION,
    MONGO_CONN_TIMEOUT_MS,
    MONGO_SOCKET_TIMEOUT_MS,
)
from .models import AnalysisResult
from .repository import Repository

def _to_document(result: AnalysisResult) -> Dict:
    return {
        "analysis_id": result.analysis_id,
        "timestamp": result.timestamp,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "query": result.query,
        "followups": result.followups,
        "pdf_path": result.pdf_path,
    }

class BaseMongoRepository(Repository):
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        self._client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=MONGO_CONN_TIMEOUT_MS,
            socketTimeoutMS=MONGO_SOCKET_TIMEOUT_MS,
        )
        self._db = self._client[db_name]
        self._col: Collection = self._db[collection_name]
        self._indexed = set()
        self._ensure_indexes(self._col)

    def _ensure_indexes(self, col: Collection) -> None:
        if col.name in self._indexed:
            return
        col.create_index([("analysis_id", ASCENDING)], unique=True, name="ix_analysis_id_unique")
        col.create_index([("created_at", DESCENDING)], name="ix_created_at")
        self._indexed.add(col.name)

    def _to_col(self, collection_name: str = None) -> Collection:
        if not collection_name:
            return self._col
        col = self._db[collection_name]
        self._ensure_indexes(col)
        return col

    def save_result(self, result: AnalysisResult) -> str:
        if not result.analysis_id or not result.analysis_id.strip():
            raise ValueError("analysis_id is required")
        doc = _to_document(result)
        col = self._to_col()
        res = col.replace_one({"analysis_id": result.analysis_id}, doc, upsert=True)
        return str(res.upserted_id) if res.upserted_id else result.analysis_id

    def save_result_to(self, collection: str, result: AnalysisResult) -> str:
        if not result.analysis_id or not result.analysis_id.strip():
            raise ValueError("analysis_id is required")
        doc = _to_document(result)
        col = self._to_col(collection)
        res = col.replace_one({"analysis_id": result.analysis_id}, doc, upsert=True)
        return str(res.upserted_id) if res.upserted_id else result.analysis_id

class StockMongoRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__(MONGO_URI, MONGO_DB_NAME, STOCKS_COLLECTION)

class SoccerMongoRepository(BaseMongoRepository):
    def __init__(self):
        super().__init__(MONGO_URI, MONGO_DB_NAME, SOCCER_COLLECTION)
