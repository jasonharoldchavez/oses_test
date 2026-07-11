import numpy as np
from .framework_core import AbstractDecisionLayer

class GeometricAcousticDetector(AbstractDecisionLayer):
    def __init__(self, channels=3):
        self.channels = channels
        self.GOLDEN_RATIO = (1 + np.sqrt(5)) / 2
        self.HARMONIC_NODES = np.array([3.1, 6.1, 9.1])
        self.baseline_mu = None
        self.inv_covariance = None
        self.is_calibrated = False

    def calibrate(self, calibration_data):
        matrix = np.array(calibration_data, dtype=float)
        self.baseline_mu = np.mean(matrix, axis=0)
        covariance = np.cov(matrix, rowvar=False)
        if self.channels == 1:
            covariance = np.array([[covariance]])
        self.inv_covariance = np.linalg.pinv(covariance + np.eye(self.channels) * 1e-6)
        self.is_calibrated = True

    def update(self, raw_signal):
        if not self.is_calibrated:
            raise ValueError("Detector must be calibrated first.")
        
        sample = np.array(raw_signal, dtype=float)
        
        # Mahalanobis Distance
        delta = sample - self.baseline_mu
        dist_sq = delta.T @ self.inv_covariance @ delta
        m_distance = float(np.sqrt(max(0.0, dist_sq)))
        
        # Spectral Entropy
        fft_vals = np.abs(np.fft.rfft(sample))
        probs = (fft_vals + 1e-9) / (np.sum(fft_vals) + 1e-9)
        entropy = -np.sum(probs * np.log(probs + 1e-9))
        
        anomaly_score = (0.5 * m_distance) + (0.2 * float(entropy))
        return {
            "anomaly_score": round(anomaly_score, 4), 
            "metrics": {
                "mahalanobis": round(m_distance, 4), 
                "entropy": round(entropy, 4)
            }
        }
