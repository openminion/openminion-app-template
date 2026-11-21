from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class RequestRecord:
    request_id: str
    prompt: str
    session_id: str
    status: str
    result_id: str = ""
    run_id: str = ""
    output: str = ""


class RequestStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    request_id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_id TEXT NOT NULL DEFAULT '',
                    run_id TEXT NOT NULL DEFAULT '',
                    output TEXT NOT NULL DEFAULT ''
                )
                """
            )

    def create(self, request_id: str, prompt: str) -> RequestRecord:
        normalized_id = request_id.strip()
        normalized_prompt = prompt.strip()
        if not normalized_id or not normalized_prompt:
            raise ValueError("request_id and prompt are required")
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO requests"
                "(request_id, prompt, session_id, status) "
                "VALUES (?, ?, ?, 'pending')",
                (normalized_id, normalized_prompt, uuid4().hex),
            )
        record = self.get(normalized_id)
        if record is None:
            raise RuntimeError("request record was not created")
        if record.prompt != normalized_prompt:
            raise ValueError("request_id already belongs to another prompt")
        return record

    def get(self, request_id: str) -> RequestRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT request_id, prompt, session_id, status, "
                "result_id, run_id, output "
                "FROM requests WHERE request_id = ?",
                (request_id.strip(),),
            ).fetchone()
        return RequestRecord(*row) if row is not None else None

    def complete(
        self,
        request_id: str,
        *,
        result_id: str,
        run_id: str,
        output: str,
    ) -> RequestRecord:
        with self._connect() as connection:
            updated = connection.execute(
                "UPDATE requests SET status = 'completed', result_id = ?, run_id = ?, "
                "output = ? WHERE request_id = ? AND status = 'pending'",
                (result_id, run_id, output, request_id),
            ).rowcount
        if updated != 1:
            raise ValueError("request is not pending")
        record = self.get(request_id)
        if record is None:
            raise RuntimeError("completed request is missing")
        return record

    def fail(self, request_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE requests SET status = 'failed' "
                "WHERE request_id = ? AND status = 'pending'",
                (request_id,),
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)
