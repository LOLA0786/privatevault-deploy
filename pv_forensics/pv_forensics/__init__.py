try:
    from .cognitive_replay_engine import (
        replay_cognitive_session,
        store_snapshot,
        CognitiveReplayResult,
        CognitiveReplayError
    )
except ImportError:
    # Fallback for current session (replay_engine not recreated in this turn)
    replay_cognitive_session = None
    store_snapshot = None
    CognitiveReplayResult = None
    CognitiveReplayError = None

from .cognitive_audit_report_generator import (
    generate_audit_report,
    AuditReport
)

__all__ = [
    'replay_cognitive_session',
    'store_snapshot',
    'CognitiveReplayResult',
    'CognitiveReplayError',
    'generate_audit_report',
    'AuditReport'
]
