import math
import pytest
from streaming_guardian import StandardizedCUSUMDetector

def test_baseline_is_frozen_after_burn_in():
    detector = StandardizedCUSUMDetector(burn_in=5, h=4.0)
    for value in (10.0, 10.2, 9.8, 10.1, 9.9):
        alarm, score = detector.update(value)
        assert not alarm and score == 0.0
    mean, std = detector.baseline_mean, detector.baseline_std
    for value in (12.0, 12.0, 12.0): detector.update(value)
    assert detector.baseline_mean == mean and detector.baseline_std == std

@pytest.mark.parametrize("shift", [5.0, -5.0])
def test_detects_positive_and_negative_shifts(shift):
    detector = StandardizedCUSUMDetector(burn_in=20, k=0.5, h=5.0)
    for value in [10.0 + (i % 2) * 0.1 for i in range(20)]: detector.update(value)
    assert any(detector.update(10.0 + shift)[0] for _ in range(5))

def test_stable_stream_does_not_alarm_after_calibration():
    detector = StandardizedCUSUMDetector(burn_in=20, h=5.0)
    values = [10.0 + ((i % 4) - 1.5) * 0.1 for i in range(20)]
    for value in values: detector.update(value)
    assert not any(detector.update(values[i % len(values)])[0] for i in range(200))

@pytest.mark.parametrize("bad", [None, True, "1", float("nan"), float("inf"), -float("inf")])
def test_invalid_observation_does_not_mutate_state(bad):
    detector = StandardizedCUSUMDetector(burn_in=3)
    detector.update(1.0)
    before = (detector.count, detector._mean, detector._m2, detector.baseline_mean, detector.baseline_std, detector.positive_sum, detector.negative_sum)
    with pytest.raises(ValueError): detector.update(bad)
    after = (detector.count, detector._mean, detector._m2, detector.baseline_mean, detector.baseline_std, detector.positive_sum, detector.negative_sum)
    assert after == before

def test_reset_restarts_calibration():
    detector = StandardizedCUSUMDetector(burn_in=3)
    for value in (1.0, 2.0, 3.0): detector.update(value)
    assert detector.ready
    detector.reset()
    assert not detector.ready and detector.count == 0 and detector.alarm_count == 0

def test_configuration_validation():
    for kwargs in ({"burn_in": True}, {"burn_in": 1}, {"k": -1}, {"h": 0}, {"min_std": 0}, {"h": math.inf}):
        with pytest.raises(ValueError): StandardizedCUSUMDetector(**kwargs)