"""Deterministic workflow failures that agents cannot override."""


class WorkflowError(RuntimeError):
    """Base class for code-owned workflow rejection."""


class IllegalTransitionError(WorkflowError):
    """The requested edge is not present in the transition table."""


class ArtifactGateError(WorkflowError):
    """A transition artifact is absent, mismatched, or semantically invalid."""


class BudgetExceededError(WorkflowError):
    """A deterministic resource charge would exceed its configured limit."""


class EventChainError(WorkflowError):
    """The append-only event sequence failed integrity validation."""
