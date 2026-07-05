import numpy as np
from streaming_guardian.detectors.framework_core import AbstractMeasurementLayer

class DynamicSensor(AbstractMeasurementLayer):
    def __init__(self, scale=0.5, drift=0.0, drift_type="gradual"):
        self.scale = scale
        self.drift = drift
        self.drift_type = drift_type
        self.step = 0
        self.base_value = 10.0

    def fetch_raw_data(self):
        self.step += 1
        noise = np.random.normal(0, self.scale)
        
        # Ground truth anomaly logic occurs at step 50
        current_drift = 0.0
        if self.step > 50:
            if self.drift_type == "gradual":
                current_drift = self.drift * (self.step - 50)
            elif self.drift_type == "step":
                current_drift = self.drift
                
        return self.base_value + current_drift + noise
