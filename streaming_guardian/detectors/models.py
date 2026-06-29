import numpy as np
from framework_core import AbstractDecisionLayer

class CUSUMDecisionEngine(AbstractDecisionLayer):
    def __init__(self, threshold_h=4.605, noise_floor=10.8):
        self.h = threshold_h
        self.floor = noise_floor
        self.tracker = 0.0

    def update(self, isolated_signal):
        increment = isolated_signal - self.floor
        self.tracker = max(0.0, self.tracker + increment)
        return self.tracker > self.h, self.tracker

class SimpleMovingAverageDetector(AbstractDecisionLayer):
    def __init__(self, window_size=15, threshold_multiplier=2.5):
        self.window_size = window_size
        self.m = threshold_multiplier
        self.history = []

    def update(self, signal):
        self.history.append(signal)
        if len(self.history) < self.window_size:
            return False, 0.0
        window = self.history[-self.window_size:]
        mean = np.mean(window)
        std = np.std(window) if np.std(window) > 0 else 0.1
        is_alarm = signal > (mean + (self.m * std))
        return is_alarm, float(signal - mean)

class EWMADetector(AbstractDecisionLayer):
    def __init__(self, alpha=0.15, threshold_multiplier=2.5):
        self.alpha = alpha
        self.m = threshold_multiplier
        self.ewma = None
        self.variance = 0.1

    def update(self, signal):
        if self.ewma is None:
            self.ewma = signal
            return False, 0.0
        self.ewma = (self.alpha * signal) + ((1.0 - self.alpha) * self.ewma)
        diff = signal - self.ewma
        self.variance = (0.1 * (diff**2)) + (0.9 * self.variance)
        limit = self.ewma + (self.m * np.sqrt(self.variance))
        is_alarm = signal > limit
        return is_alarm, float(diff)
