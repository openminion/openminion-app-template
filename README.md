# OpenMinion application template

A small Python application that keeps product state in its own SQLite database
and uses the public OpenMinion SDK for agent execution.

## Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
openminion setup --no-chat
openminion-app "Draft a short launch checklist"
pytest
```

Set `OPENMINION_CONFIG` to an explicit `agents.json`, or pass `--config`.
`OPENMINION_AGENT` selects a configured agent profile. The application does
not copy provider keys or runtime policy into its own settings.

## Boundary

- `domain.py` owns application requests and the SQLite mapping to runtime IDs.
- `runtime.py` owns one shared `APIRuntime` and uses public SDK imports.
- `workflows.py` coordinates one request-to-result flow.
- `tools.py` and `prompts.py` are application-owned behavior.
- `evals/` is separate from deterministic unit tests.

An exact duplicate request returns its recorded result. Reusing the request ID
with another prompt fails. A failed or uncertain external action is not
automatically replayed. OpenMinion sessions, policy, tools, and telemetry remain
owned by OpenMinion.

The maintained dependency range is `openminion>=0.1.24,<0.2`. CI tests the
exact released package and an exact OpenMinion `dev` revision independently.
The template is an educational starting point, not a hosted multi-tenant
platform or production support promise.

For an opt-in configured-provider smoke:

```bash
OPENMINION_LIVE_CONFIG=/path/to/agents.json pytest -m live
```
