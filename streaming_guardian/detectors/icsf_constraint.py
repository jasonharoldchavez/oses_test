import numpy as np
from typing import Dict, Any, Union
import logging

from .framework_core import AbstractDecisionLayer

logger = logging.getLogger("streaming_guardian.icsf")

class ICSFConstraintDetector(AbstractDecisionLayer):
    """
    Production-Grade Unified ICSF Constraint Engine.
    Features input sanitization, dynamic horizons, and pattern tracking.
    """
    def __init__(self, lock_limit: float = 1.0, alpha_decay: float = 0.40):
        self.g_state: np.ndarray = np.array([3.1, 6.1, 9.1], dtype=float)
        self.lock_limit: float = lock_limit
        self.alpha_decay: float = alpha_decay
        self.running_penalty: float = 0.0
        self.history = []

    def _nearest_symbol(self, value: float) -> str:
        if value < 4.5: return "3"
        if value < 7.5: return "6"
        return "9"

    def _analyze_patterns(self, vec: np.ndarray) -> list:
        patterns = []
        if len(self.history) < 2:
            return patterns
            
        prev = self.history[-1]
        jump = float(np.linalg.norm(vec - prev))
        if jump > 2.0:
            patterns.append({"type": "anomaly", "score": jump, "note": "sudden jump"})
            
        if len(self.history) >= 4:
            diffs = [float(np.sum(self.history[i] - self.history[i-1])) for i in range(-3, 0)]
            if all(d > 0.0 for d in diffs):
                patterns.append({"type": "motif", "name": "increasing_trend"})
            elif all(d < 0.0 for d in diffs):
                patterns.append({"type": "motif", "name": "decreasing_trend"})
        return patterns

    def update(self, raw_signal: Union[list, np.ndarray]) -> Dict[str, Any]:
        # Clean and validate input structure
        vec = np.array(raw_signal, dtype=float)
        if vec.shape != (3,):
            raise ValueError("Input vector must be a 3-element spatial array.")
            
        # Production Sanitization Gate: Protect against bad telemetry data
        if not np.isfinite(vec).all():
            logger.error(f"Malformed telemetry received: {vec}")
            return {
                "status": "TSLP_LOCKOUT_INITIATED",
                "penalty_score": round(self.running_penalty, 4),
                "note": "CRITICAL_TELEMETRY_CORRUPTION_DETECTED"
            }
            
        # 1. Cubic Deviation & Decay Math
        deviations = np.abs(vec - self.g_state)
        instant_penalty = float(np.sum(np.power(deviations, 3)))
        self.running_penalty = (self.alpha_decay * self.running_penalty) + ((1.0 - self.alpha_decay) * instant_penalty)
        
        # 2. Horizon Tracking
        self.history.append(vec)
        if len(self.history) > 30:
            self.history.pop(0)
            
        drift_rate = float(np.linalg.norm(vec - self.history[0])) / len(self.history)
        projected_growth = 1.0 + min(5.0, drift_rate * 0.1)
        projected_penalty = self.running_penalty * (projected_growth ** 3)
        
        # 3. Features & Symbols
        detected_patterns = self._analyze_patterns(vec)
        symbol_chain = f"{self._nearest_symbol(vec[0])}-{self._nearest_symbol(vec[1])}-{self._nearest_symbol(vec[2])}"
        
        # 4. State Machine Evaluation
        if projected_penalty > self.lock_limit or self.running_penalty > self.lock_limit:
            status = "TSLP_LOCKOUT_INITIATED"
        elif self.running_penalty >= 0.5 * self.lock_limit:
            status = "RECOMMEND_ESCALATION"
        else:
            status = "SYSTEM_ALIGNED"
            
        return {
            "status": status,
            "penalty_score": round(self.running_penalty, 4),
            "projected_penalty_3_steps": round(projected_penalty, 4),
            "symbolic_chain": symbol_chain,
            "patterns": detected_patterns,
            "channel_errors": [round(float(d), 4) for d in deviations]
        }
