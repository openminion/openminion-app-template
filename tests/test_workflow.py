from __future__ import annotations

import logging
from pathlib import Path

import pytest

from openminion_app_template.domain import RequestStore
from openminion_app_template.runtime import RuntimeReply
from openminion_app_template.workflows import ApplicationWorkflow


class FakeRuntime:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run(self, prompt: str, *, session_id: str) -> RuntimeReply:
        self.calls.append((prompt, session_id))
        return RuntimeReply("result-1", "run-1", f"answer: {prompt}")


def test_request_is_mapped_and_exact_duplicate_is_reused(tmp_path: Path) -> None:
    runtime = FakeRuntime()
    workflow = ApplicationWorkflow(RequestStore(tmp_path / "app.db"), runtime)

    first = workflow.execute("request-1", "hello")
    second = workflow.execute("request-1", "hello")

    assert first == second
    assert first.status == "completed"
    assert (first.result_id, first.run_id) == ("result-1", "run-1")
    assert len(runtime.calls) == 1


def test_conflicting_duplicate_is_rejected(tmp_path: Path) -> None:
    workflow = ApplicationWorkflow(RequestStore(tmp_path / "app.db"), FakeRuntime())
    workflow.execute("request-1", "first")

    with pytest.raises(ValueError, match="another prompt"):
        workflow.execute("request-1", "second")


def test_restart_reads_mapping_without_cross_record_leakage(tmp_path: Path) -> None:
    path = tmp_path / "app.db"
    workflow = ApplicationWorkflow(RequestStore(path), FakeRuntime())
    first = workflow.execute("request-1", "first")
    workflow.execute("request-2", "second")

    restarted = RequestStore(path)
    assert restarted.get("missing") is None
    assert restarted.get("request-1") == first
    assert restarted.get("request-1").output == "answer: first"
    assert restarted.get("request-2").output == "answer: second"


def test_failure_records_status_without_logging_prompt(tmp_path: Path, caplog) -> None:
    class FailingRuntime:
        def run(self, prompt: str, *, session_id: str) -> RuntimeReply:
            del prompt, session_id
            raise RuntimeError("provider unavailable")

    store = RequestStore(tmp_path / "app.db")
    with caplog.at_level(logging.INFO), pytest.raises(RuntimeError):
        ApplicationWorkflow(store, FailingRuntime()).execute(
            "request-1", "secret prompt"
        )

    assert store.get("request-1").status == "failed"
    assert "secret prompt" not in caplog.text
