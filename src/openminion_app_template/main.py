from __future__ import annotations

import argparse
import os
from uuid import uuid4

from .domain import RequestStore
from .runtime import OpenMinionRuntime
from .workflows import ApplicationWorkflow


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one OpenMinion app request.")
    parser.add_argument("prompt")
    parser.add_argument("--request-id", default=None)
    parser.add_argument("--config", default=os.getenv("OPENMINION_CONFIG"))
    parser.add_argument("--agent", default=os.getenv("OPENMINION_AGENT"))
    parser.add_argument("--db", default=os.getenv("OPENMINION_APP_DB", "var/app.db"))
    args = parser.parse_args()

    runtime = OpenMinionRuntime(config_path=args.config, agent_id=args.agent)
    try:
        record = ApplicationWorkflow(RequestStore(args.db), runtime).execute(
            args.request_id or uuid4().hex,
            args.prompt,
        )
    finally:
        runtime.close()
    print(record.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
