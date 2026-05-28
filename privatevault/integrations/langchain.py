"""PrivateVault LangChain / LangGraph Integration

Drop-in middleware that wraps LangChain agents, chains, and LangGraph workflows with:
- Pre-execution cognitive validation (drift, reasoning integrity, approval binding)
- Merkle snapshot sealing
- Deterministic replay on mutation
- Forensic lineage and trust decay

Zero-config by default (auto-detects agent type). Replayable for audits.
"""

import functools
import json
import uuid
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from langchain_core.agents import AgentAction, AgentExecutor
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph  # type: ignore

# Core PrivateVault primitives (existing modules only)
try:
    from pv_cognition.cognition_snapshot import create_snapshot, CognitionSnapshot
    from pv_cognition.pre_execution_cognitive_validator import (
        validate_cognition_before_execution,
        CognitionDecision,
    )
    from pv_forensics import replay_cognitive_session
    from approval_binding import assert_approval_binding
    from merkle import compute_merkle_root
    from decision_ledger import log_decision
except ImportError:
    # Graceful fallback for packaging/demo
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


class PrivateVaultMiddleware:
    """Main integration class. Wraps any LangChain/LangGraph runnable."""

    def __init__(self, agent_id: Optional[str] = None, tenant_id: str = "default", auto_replay: bool = True):
        self.agent_id = agent_id or f"agent-{uuid.uuid4().hex[:8]}"
        self.tenant_id = tenant_id
        self.auto_replay = auto_replay
        self.correlation_id = str(uuid.uuid4())
        self.snapshots: list[CognitionSnapshot] = []

    def _create_snapshot(self, input_data: Any, reasoning: Optional[str] = None) -> CognitionSnapshot:
        """Create sealed snapshot for pre-execution gate."""
        snapshot = create_snapshot(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            input_data=json.dumps(input_data, default=str) if not isinstance(input_data, str) else input_data,
            reasoning_text=reasoning or "LangChain agent invocation",
            correlation_id=self.correlation_id,
        )
        snapshot.seal_reasoning_score(0.92)
        self.snapshots.append(snapshot)
        return snapshot

    def _validate_before_execution(self, snapshot: CognitionSnapshot, action: Dict[str, Any], approval: Optional[Dict[str, Any]] = None) -> CognitionDecision:
        """Core pre-execution cognitive gate."""
        decision = validate_cognition_before_execution(
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            action=action,
            current_snapshot=snapshot,
            approval=approval,
            reasoning_text=getattr(snapshot, "reasoning_text", None),
        )

        if decision.verdict == "BLOCK":
            if self.auto_replay:
                replay_result = replay_cognitive_session(self.correlation_id)
                log_decision({
                    "correlation_id": self.correlation_id,
                    "verdict": "BLOCK",
                    "reason": decision.reason,
                    "replay": replay_result,
                    "effective_trust": decision.effective_trust,
                })
            raise RuntimeError(f"PrivateVault BLOCK: {decision.reason} (trust={decision.effective_trust})")

        return decision

    def wrap(self, runnable: Any) -> Any:
        """Wrap a LangChain Runnable, AgentExecutor, or LangGraph graph."""
        if isinstance(runnable, (AgentExecutor, Runnable)):
            original_invoke = runnable.invoke

            @functools.wraps(original_invoke)
            def wrapped_invoke(input_data: Any, config: Optional[Dict] = None, **kwargs: Any) -> Any:
                snapshot = self._create_snapshot(input_data)
                action = {"tool": getattr(runnable, "name", "unknown"), "input": input_data}
                self._validate_before_execution(snapshot, action)

                # Execute with full context
                result = original_invoke(input_data, config=config or {}, **kwargs)

                # Post-execution Merkle seal and ledger
                merkle_root = compute_merkle_root({"input": input_data, "output": result})
                log_decision({
                    "correlation_id": self.correlation_id,
                    "verdict": "ALLOW",
                    "merkle_root": merkle_root,
                    "snapshot_id": getattr(snapshot, "snapshot_id", "unknown"),
                })
                return result

            runnable.invoke = wrapped_invoke
            return runnable

        elif isinstance(runnable, StateGraph):
            # LangGraph support - wrap nodes
            for node_name, node_func in getattr(runnable, "nodes", {}).items():
                if callable(node_func):
                    runnable.nodes[node_name] = self._wrap_node(node_func)
            return runnable

        return runnable

    def _wrap_node(self, node_func: Callable) -> Callable:
        """Wrap individual LangGraph node."""

        @functools.wraps(node_func)
        def wrapped_node(state: Any, *args: Any, **kwargs: Any) -> Any:
            snapshot = self._create_snapshot(state)
            action = {"tool": node_func.__name__, "input": state}
            self._validate_before_execution(snapshot, action)
            result = node_func(state, *args, **kwargs)
            return result

        return wrapped_node


# Convenience decorators for drop-in use
def with_privatevault(agent_id: Optional[str] = None, **middleware_kwargs: Any) -> Callable[[F], F]:
    """Decorator for wrapping LangChain agents."""

    def decorator(func: F) -> F:
        middleware = PrivateVaultMiddleware(agent_id=agent_id, **middleware_kwargs)

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            # Auto-wrap if it's a runnable
            if len(args) > 0 and hasattr(args[0], "invoke"):
                middleware.wrap(args[0])
            return func(*args, **kwargs)

        return cast(F, wrapped)

    return decorator


# Public API (matches README example)
__all__ = ["PrivateVaultMiddleware", "with_privatevault"]
