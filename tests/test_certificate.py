import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from benchmarks.generate_certificate import generate_certificate


class CertificateTests(unittest.TestCase):
    def test_report_generates_with_real_input_rejection_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("os.getcwd", return_value=directory):
                previous = os.getcwd()
                os.chdir(directory)
                try:
                    generate_certificate()
                    report = Path("MODEL_BEHAVIOR_CERTIFICATE.txt").read_text(encoding="utf-8")
                finally:
                    os.chdir(previous)
        self.assertIn("Malformed-input rejection: PASSED (5/5 rejected)", report)
        self.assertIn("Seeded generator reproducibility smoke check: PASSED", report)
        self.assertIn("not a calibrated false-alarm probability", report)


if __name__ == "__main__":
    unittest.main()
