import os
import sqlite3
import json
from typing import Any, Optional
from app.repository.abstract_db_operations import AbstractDBOperations


class OpenAIDB(AbstractDBOperations):
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.environ.get("OPENAI_DB_PATH", "open_ai_db.sqlite")
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    payload TEXT,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def create(self, data: Any) -> Any:
        """
        Create a new record with status 'pending'.
        Expects data to have 'id', 'payload', and optionally 'status' and 'result'.
        """
        import datetime

        record_id = data.get("id")
        payload = data.get("payload")
        status = data.get("status", "pending")
        result = data.get("result")
        if record_id is None:
            raise ValueError("Data must contain an 'id' field.")
        payload_json = json.dumps(payload) if payload is not None else None
        result_json = json.dumps(result) if result is not None else None
        created_at = datetime.datetime.utcnow().isoformat()
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO records (id, status, payload, result, created_at) VALUES (?, ?, ?, ?, ?)",
                (record_id, status, payload_json, result_json, created_at),
            )
        return {
            "id": record_id,
            "status": status,
            "payload": payload,
            "result": result,
            "created_at": created_at,
        }

    def get(self, query: Any) -> Optional[Any]:
        """
        Read a record by id.
        Returns a dict with id, status, payload, and result.
        """
        cursor = self.conn.execute(
            "SELECT id, status, payload, result FROM records WHERE id = ?", (query,)
        )
        row = cursor.fetchone()
        if row:
            payload = json.loads(row[2]) if row[2] else None
            result = json.loads(row[3]) if row[3] else None
            return {
                "id": row[0],
                "status": row[1],
                "payload": payload,
                "result": result,
            }
        return None

    def delete(self, identifier: Any) -> bool:
        """
        Delete a record by id.
        """
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM records WHERE id = ?", (identifier,)
            )
        return cursor.rowcount > 0

    def update_status_and_result(self, record_id: str, status: str, result: Any = None):
        """
        Update the status and result of a record.
        """
        result_json = json.dumps(result) if result is not None else None
        with self.conn:
            self.conn.execute(
                "UPDATE records SET status = ?, result = ? WHERE id = ?",
                (status, result_json, record_id),
            )

    def delete_older_than_minutes(self, minutes: int) -> int:
        """
        Delete all records older than the specified number of minutes.
        Returns the number of deleted records.
        """
        import datetime

        cutoff = (
            datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        ).isoformat()
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM records WHERE created_at < ?", (cutoff,)
            )
        return cursor.rowcount
