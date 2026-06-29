import pytest
import numpy as np
from streaming_guardian import AdaptiveCUSUMDetector

def test_detector_burn_in():
    detector = AdaptiveCUSUMDetector(burn_in=30)
    for _ in range(30):
        is_alarm, _ = detector.update(10.0)
        assert not is_alarm

def test_detector_anomaly_response():
    detector = AdaptiveCUSUMDetector(burn_in=5)
    for _ in range(5):
        detector.update(10.0)
    
    is_alarm, tracker = detector.update(100.0)
    assert is_alarm
    assert tracker > 0.0
