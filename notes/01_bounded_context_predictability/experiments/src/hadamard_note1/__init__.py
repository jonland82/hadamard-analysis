"""Bounded-context prediction experiments for Hadamard matrices."""

from .contexts import ObservationBatch, extract_contexts
from .evaluation import evaluate_context_model
from .matrices import normalize_hadamard, require_hadamard, sylvester
from .models import SmoothedContextModel

__all__ = [
    "ObservationBatch",
    "SmoothedContextModel",
    "evaluate_context_model",
    "extract_contexts",
    "normalize_hadamard",
    "require_hadamard",
    "sylvester",
]
