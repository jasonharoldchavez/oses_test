import unittest

from benchmarks.benchmark_runner import run_statistical_audit


class BenchmarkRunnerValidationTests(unittest.TestCase):
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
