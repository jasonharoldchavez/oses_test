import math
import unittest

from benchmarks.metrics import summarize_trials


class BenchmarkMetricTests(unittest.TestCase):
    def test_trial_and_sample_metrics_use_distinct_denominators(self):
        metrics = summarize_trials(
            num_trials=4,
            change_point=5,
            false_alarm_counts=[0, 2, 0, 1],
            detection_delays=[0, 3],
        )
        self.assertEqual(metrics["false_alarm_trial_probability"], 0.5)
        self.assertEqual(metrics["false_alarm_sample_rate"], 3 / 20)
        self.assertEqual(metrics["detection_probability"], 0.5)
        self.assertEqual(metrics["mean_delay_given_detection"], 1.5)
        self.assertEqual(metrics["false_alarm_trials"], 2)
        self.assertEqual(metrics["false_alarm_samples"], 3)
        self.assertEqual(metrics["pre_change_samples"], 20)

    def test_no_detections_are_not_reported_as_zero_delay(self):
        metrics = summarize_trials(2, 10, [0, 0], [])
        self.assertTrue(math.isnan(metrics["mean_delay_given_detection"]))
        self.assertEqual(metrics["detection_probability"], 0.0)

    def test_invalid_metric_inputs_rejected(self):
        cases = [
            (0, 5, [], []),
            (2, 0, [0, 0], []),
            (2, 5, [0], []),
            (2, 5, [-1, 0], []),
            (2, 5, [0, 0], [-1]),
            (2, 5, [0, 0], [0, 1, 2]),
        ]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    summarize_trials(*args)


if __name__ == "__main__":
    unittest.main()
