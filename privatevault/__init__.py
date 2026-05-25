"""PrivateVault Runtime Package.

Canonical entrypoint for governance runtime.
All execution must flow through GovernanceRuntime.
"""

try:
    from governance_runtime import get_governance_runtime, GovernanceRuntime, ExecutionLineage, ExecutionContext
except ImportError:
    from .core.governance_runtime import get_governance_runtime, GovernanceRuntime, ExecutionLineage
    ExecutionContext = dict  # shim
from .core.execution_entrypoint import ExecutionEntrypoint

__all__ = ["get_governance_runtime", "GovernanceRuntime", "ExecutionLineage", "ExecutionContext", "ExecutionEntrypoint"]

# Compatibility shim for legacy imports
try:
    from ..policy_engine import authorize_intent
except ImportError:
    authorize_intent = None
