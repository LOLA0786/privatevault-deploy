"""PrivateVault CrewAI Integration

Adapter for CrewAI agents and crews. Mirrors the LangChain middleware pattern for consistency.
Uses the same Cognitive pre-execution gate, Merkle snapshots, and deterministic replay.
"""

import functools
import uuid
from typing import Any, Callable, Dict, Optional, TypeVar, cast

try:
    from crewai import Agent, Task, Crew  # type: ignore
except ImportError:
    class Crew:  # type: ignore
        pass
    class Agent:  # type: ignore
        pass
    class Task:  # type: ignore
        pass

# Reuse core primitives (same as langchain.py)
try:
    from pv_cognition.cognition_snapshot import create_snapshot, CognitionSnapshot
    from pv_cognition.pre_execution_cognitive_validator import validate_cognition_before_execution
    from pv_forensics import replay_cognitive_session
    from approval_binding import assert_approval_binding
    from merkle import compute_merkle_root
    from decision_ledger import log_decision
except ImportError:
    class CognitionSnapshot:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)
        def seal_reasoning_score(self, score: float = 0.85) -> None:
            self.reasoning_integrity_score = score

    def create_snapshot(**kwargs: Any) -> CognitionSnapshot:
        return CognitionSnapshot(**kwargs)

    def validate_cognition_before_execution(*args: Any, **kwargs: Any) -> Any:
        return type("Decision", (), {"verdict": "ALLOW", "effective_trust": 0.85, "reason": "demo"})()

    def replay_cognitive_session(correlation_id: str) -> Dict[str, Any]:
        return {"correlation_id": correlation_id, "verdict": "BLOCK", "trust_trajectory": [0.92, 0.19]}

    def assert_approval_binding(*args: Any, **kwargs: Any) -> bool:
        return True

    def compute_merkle_root(data: Any) -> str:
        return "mock_merkle_root"

    def log_decision(event: Dict[str, Any]) -> None:
        pass


F = TypeVar("F", bound=Callable[..., Any])


class PrivateVaultCrewMiddleware:
    """CrewAI specific wrapper. Delegates to shared logic where possible."""

    def __init__(self, agent_id: Optional[str] = None, tenant_id: str = "default"):
        self.agent_id = agent_id or f"crew-{uuid.uuid4().hex[:8]}"
        self.tenant_id = tenant_id
        self.correlation_id = str(uuid.uuid4())

    def wrap_crew(self, crew: Any) -> Any:
        """Wrap a CrewAI Crew instance."""
        if hasattr(crew, "kickoff"):
            original_kickoff = crew.kickoff

            @functools.wraps(original_kickoff)
            def wrapped_kickoff(*args: Any, **kwargs: Any) -> Any:
                # Create snapshot for the entire crew run
                snapshot = create_snapshot(
                    agent_id=self.agent_id,
                    tenant_id=self.tenant_id,
                    input_data=str(kwargs.get("inputs", args[0] if args else {})),
                    reasoning_text="CrewAI multi-agent execution",
                    correlation_id=self.correlation_id,
                )
                snapshot.seal_reasoning_score(0.92)

                # Pre-execution validation (uses same gate as LangChain)
                decision = validate_cognition_before_execution(
                    agent_id=self.agent_id,
                    tenant_id=self.tenant_id,
                    action={"tool": "crew_kickoff", "input": kwargs},
                    current_snapshot=snapshot,
                )

                if decision.verdict == "BLOCK":
                    replay_result = replay_cognitive_session(self.correlation_id)
                    log_decision({
                        "correlation_id": self.correlation_id,
                        "verdict": "BLOCK",
                        "reason": decision.reason,
                        "replay": replay_result,
                        "effective_trust": getattr(decision, "effective_trust", 0.19),
                    })
                    raise RuntimeError(f"PrivateVault BLOCKED CrewAI execution: {decision.reason}")

                result = original_kickoff(*args, **kwargs)

                # Post-execution forensic seal
                merkle_root = compute_merkle_root({"crew_result": str(result)})
                log_decision({
                    "correlation_id": self.correlation_id,
                    "verdict": "ALLOW",
                    "merkle_root": merkle_root,
                    "snapshot_id": getattr(snapshot, "snapshot_id", "unknown"),
                })
                return result

            crew.kickoff = wrapped_kickoff
        return crew


# Drop-in decorator
def with_privatevault_crew(agent_id: Optional[str] = None, **kwargs: Any) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        middleware = PrivateVaultCrewMiddleware(agent_id=agent_id, **kwargs)

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if len(args) > 0 and isinstance(args[0], (Crew, Agent, Task)):
                middleware.wrap_crew(args[0])
            return func(*args, **kwargs)
        return cast(F, wrapped)
    return decorator


__all__ = ["PrivateVaultCrewMiddleware", "with_privatevault_crew"]
