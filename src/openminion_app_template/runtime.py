from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from openminion import Agent, APIRuntime


@dataclass(frozen=True)
class RuntimeReply:
    result_id: str
    run_id: str
    text: str


class RuntimeClient(Protocol):
    def run(self, prompt: str, *, session_id: str) -> RuntimeReply: ...


class OpenMinionRuntime:
    def __init__(self, *, config_path: str | None, agent_id: str | None) -> None:
        self.runtime = APIRuntime.from_config_path(config_path)
        self.agent_id = agent_id

    def run(self, prompt: str, *, session_id: str) -> RuntimeReply:
        with Agent(
            runtime=self.runtime,
            agent_id=self.agent_id,
            session_id=session_id,
        ) as agent:
            result = agent.run(prompt)
        return RuntimeReply(
            result_id=result.id,
            run_id=result.run_id or "",
            text=result.text,
        )

    def close(self) -> None:
        self.runtime.close()
