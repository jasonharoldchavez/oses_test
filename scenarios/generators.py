import numpy as np
from framework_core import AbstractMeasurementLayer

class DynamicSensor(AbstractMeasurementLayer):
    def __init__(self, scale=0.4, drift=0.10, drift_type="gradual"):
        self.step = 0
        self.scale = scale
        self.drift = drift
        self.drift_type = drift_type
        
    def fetch_raw_data(self):
        self.step += 1
        noise = np.random.normal(loc=10.0, scale=self.scale)
        
        if self.step >= 50:
            if self.drift_type == "gradual":
                return noise + ((self.step - 50) * self.drift)
            elif self.drift_type == "step":
                return noise + self.drift
        return noise
