import time
import sys
import numpy as np
from abc import ABC, abstractmethod

# =====================================================================
# 1. CORE FRAMEWORK INTERFACES (Stable Blueprints)
# =====================================================================

class AbstractMeasurementLayer(ABC):
    @abstractmethod
    def fetch_raw_data(self):
        pass

class AbstractFeatureLayer(ABC):
    @abstractmethod
    def transform(self, raw_telemetry):
        pass

class AbstractDecisionLayer(ABC):
    @abstractmethod
    def update(self, isolated_signal):
        pass

class PassThroughFeature(AbstractFeatureLayer):
    def transform(self, raw_telemetry):
        return raw_telemetry

# =====================================================================
# 2. THE SELF-CORRECTING ADAPTIVE DETECTION ENGINE
# =====================================================================

class AdaptiveCUSUMDetector(AbstractDecisionLayer):
    """
    A self-correcting CUSUM engine that automatically updates its own
    noise floor based on rolling background statistics, eliminating the
    need for pre-calibrated baseline knowledge.
    """
    def __init__(self, burn_in=30):
        self.burn_in = burn_in
        self.history = []
        self.tracker = 0.0
        self.floor = 0.0
        self.h = 4.605
        self.step = 0

    def update(self, signal):
        self.step += 1
        self.history.append(signal)

        # Burn-in phase: Collect baseline data to self-calibrate
        if self.step <= self.burn_in:
            if self.step == self.burn_in:
                self.floor = np.mean(self.history) + (0.5 * np.std(self.history))
            return False, 0.0

        # Self-correction: Slowly adapt the floor if no anomaly is accumulating
        if self.tracker == 0.0:
            recent_window = self.history[-15:]
            self.floor = (0.95 * self.floor) + (0.05 * (np.mean(recent_window) + 0.5 * np.std(recent_window)))

        # Run sequential accumulation with the self-corrected baseline
        increment = signal - self.floor
        self.tracker = max(0.0, self.tracker + increment)
        return self.tracker > self.h, self.tracker
