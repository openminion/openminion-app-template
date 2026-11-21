from __future__ import annotations

import os
from pathlib import Path

import pytest

from openminion_app_template.domain import RequestStore
from openminion_app_template.runtime import OpenMinionRuntime
from openminion_app_template.workflows import ApplicationWorkflow


@pytest.mark.live
def test_configured_provider_smoke(tmp_path: Path) -> None:
    config_path = os.getenv("OPENMINION_LIVE_CONFIG")
    if not config_path:
        pytest.skip("OPENMINION_LIVE_CONFIG is not set")
    runtime = OpenMinionRuntime(config_path=config_path, agent_id=None)
    try:
        workflow = ApplicationWorkflow(RequestStore(tmp_path / "app.db"), runtime)
        result = workflow.execute("live-smoke", "Reply with exactly: template smoke ok")
    finally:
        runtime.close()
    assert result.status == "completed"
    assert result.output.strip()
