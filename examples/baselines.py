import numpy as np

class SimpleMovingAverageDetector:
    """Baseline 1: Standard rolling window average threshold."""
    def __init__(self, window_size=10, threshold_multiplier=3.0):
        self.window_size = window_size
        self.m = threshold_multiplier
        self.history = []

    def update(self, signal):
        self.history.append(signal)
        if len(self.history) < self.window_size:
            return False, 0.0
            
        # Maintain rolling window
        window = self.history[-self.window_size:]
        mean = np.mean(window)
        std = np.std(window) if np.std(window) > 0 else 0.1
        
        # Simple threshold rule
        is_alarm = signal > (mean + (self.m * std))
        return is_alarm, float(signal - mean)

class EWMADetector:
    """Baseline 2: Exponentially Weighted Moving Average tracking."""
    def __init__(self, alpha=0.2, threshold_multiplier=3.0):
        self.alpha = alpha
        self.m = threshold_multiplier
        self.ewma = None
        self.variance = 0.1

    def update(self, signal):
        if self.ewma is None:
            self.ewma = signal
            return False, 0.0
            
        # Recursive EWMA update formulas
        self.ewma = (self.alpha * signal) + ((1.0 - self.alpha) * self.ewma)
        diff = signal - self.ewma
        self.variance = (0.1 * (diff**2)) + (0.9 * self.variance)
        
        limit = self.ewma + (self.m * np.sqrt(self.variance))
        is_alarm = signal > limit
        return is_alarm, float(diff)
