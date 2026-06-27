import unittest
import numpy as np
from framework_core import AdaptiveCUSUMDetector

class TestEnterpriseCUSUMEngine(unittest.TestCase):
    
    def setUp(self):
        """Initialize a fresh detector configuration for every isolated test."""
        self.burn_in = 30
        self.detector = AdaptiveCUSUMDetector(burn_in=self.burn_in)
        
    def test_calibration_phase_accumulation(self):
        """Verify the system correctly accumulates baselines during burn-in without alerting."""
        # Feed stable normal noise
        for _ in range(self.burn_in - 1):
            alert, value = self.detector.update(np.random.normal(100, 1))
            self.assertFalse(alert, "System incorrectly triggered an alert during active calibration.")
            
    def test_drift_detection_precision(self):
        """Prove the mathematical engine catches a sudden structural data shift immediately."""
        # Complete calibration phase
        for _ in range(self.burn_in):
            self.detector.update(10.0)
            
        # Inject an undeniable process anomaly
        alert = False
        for _ in range(5):
            is_anomaly, _ = self.detector.update(25.0)  # Sudden extreme shift upward
            if is_anomaly:
                alert = True
                break
                
        self.assertTrue(alert, "Mathematical engine failed to isolate a critical data stream anomaly.")

if __name__ == '__main__':
    unittest.main()
