from __future__ import annotations

from .domain import RequestRecord, RequestStore
from .runtime import RuntimeClient


class ApplicationWorkflow:
    def __init__(self, store: RequestStore, runtime: RuntimeClient) -> None:
        self.store = store
        self.runtime = runtime

    def execute(self, request_id: str, prompt: str) -> RequestRecord:
        record = self.store.create(request_id, prompt)
        if record.status == "completed":
            return record
        if record.status != "pending":
            raise ValueError(f"request cannot run from status {record.status}")
        try:
            reply = self.runtime.run(record.prompt, session_id=record.session_id)
        except Exception:
            self.store.fail(record.request_id)
            raise
        return self.store.complete(
            record.request_id,
            result_id=reply.result_id,
            run_id=reply.run_id,
            output=reply.text,
        )
