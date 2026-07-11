import numpy as np
from .framework_core import AbstractDecisionLayer

class LuminaResonanceDetector(AbstractDecisionLayer):
    def __init__(self, target_prime=9.1):
        self.t_prime = target_prime
        self.baseline_weights = None
        self.history = []

    def calibrate(self, initial_weights):
        """Locks in the starting base configuration of the Cognitive Matrix."""
        self.baseline_weights = np.array(initial_weights, dtype=float)

    def update(self, current_weights):
        """Monitors weight shifts and flags extreme volatility or decay."""
        if self.baseline_weights is None:
            raise ValueError("Detector must be calibrated with initial weights first.")
            
        w = np.array(current_weights, dtype=float)
        
        # Calculate deviation from the baseline matrix
        deviation = float(np.linalg.norm(w - self.baseline_weights))
        
        # Calculate saturation score relative to T-Prime bounds
        saturation = float(np.mean(w) / self.t_prime)
        
        self.history.append(deviation)
        
        status = "NOMINAL"
        if deviation > 2.5:
            status = "VOLATILE_SHIFT"
        elif saturation > 0.95:
            status = "SATURATION_CRITICAL"
            
        return {
            "status": status,
            "matrix_deviation": round(deviation, 4),
            "saturation_ratio": round(saturation, 4)
        }
