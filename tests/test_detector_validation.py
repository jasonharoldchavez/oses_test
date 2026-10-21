import math
import unittest

from streaming_guardian import AdaptiveCUSUMDetector


class DetectorValidationTests(unittest.TestCase):
    def test_invalid_burn_in_rejected(self):
        for value in (0, 1, -1, 2.5, True, "30", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    AdaptiveCUSUMDetector(burn_in=value)

    def test_malformed_samples_rejected_without_mutating_state(self):
        bad_values = (None, "CORRUPT_SIGNAL", float("nan"), float("inf"),
                      float("-inf"), True, [1.0], complex(1, 2))
        for bad_value in bad_values:
            detector = AdaptiveCUSUMDetector(burn_in=3)
            detector.update(10.0)
            before = (detector.step, list(detector.history), detector.tracker, detector.floor)
            with self.subTest(value=repr(bad_value)):
                with self.assertRaises(ValueError):
                    detector.update(bad_value)
                after = (detector.step, list(detector.history), detector.tracker, detector.floor)
                self.assertEqual(after, before)

    def test_valid_finite_scalars_are_accepted(self):
        detector = AdaptiveCUSUMDetector(burn_in=3)
        for value in (10, 10.5, -2.0):
            alarm, score = detector.update(value)
            self.assertFalse(alarm)
            self.assertEqual(score, 0.0)
        self.assertEqual(detector.step, 3)
        self.assertTrue(math.isfinite(detector.floor))


if __name__ == "__main__":
    unittest.main()
