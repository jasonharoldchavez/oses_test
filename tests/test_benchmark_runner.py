import unittest
import io
from contextlib import redirect_stdout

from benchmarks.benchmark_runner import run_statistical_audit


class BenchmarkRunnerValidationTests(unittest.TestCase):
    def test_small_benchmark_reports_independent_no_change_metrics(self):
        output = io.StringIO()
        with redirect_stdout(output):
            run_statistical_audit(num_trials=2, stream_length=8, change_point=3, seed=7)
        report = output.getvalue()
        self.assertIn("No-change false-alarm probability", report)
        self.assertIn("Wilson 95% CI", report)
        self.assertIn("No-change alarm-sample rate", report)
        self.assertIn("Empirical results only", report)

    def test_invalid_configuration_fails_before_running_trials(self):
        cases = [
            {"num_trials": 0},
            {"num_trials": True},
            {"stream_length": 2},
            {"stream_length": True},
            {"change_point": 1},
            {"change_point": 120, "stream_length": 120},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    run_statistical_audit(**kwargs)


if __name__ == "__main__":
    unittest.main()
