import numpy as np
import time
from streaming_guardian.detectors.icsf_constraint import ICSFConstraintDetector

# Mock an older version behavior (Pure ICSF without Horizon/Patterns)
class BaselineICSF:
    def __init__(self):
        self.g_state = np.array([3.1, 6.1, 9.1])
        self.lock_limit = 1.0
    def update(self, raw_signal):
        vec = np.array(raw_signal, dtype=float)
        deviations = np.abs(vec - self.g_state)
        penalty = float(np.sum(np.power(deviations, 3)))
        return "TSLP_LOCKOUT_INITIATED" if penalty > self.lock_limit else "SYSTEM_ALIGNED"

# Run comparison
baseline = BaselineICSF()
experimental = ICSFConstraintDetector(lock_limit=1.0)

# Simulate a gradual drift vector stream
test_stream = [[3.1 + (i * 0.05), 6.1, 9.1] for i in range(25)]

print("=== RUNNING COMPARATIVE LIVE DRIFT AUDIT ===")
print(f"{'STEP':<6} | {'BASELINE STATUS':<20} | {'EXPERIMENTAL STATUS':<25} | {'EXP PENALTY':<12}")
print("-" * 75)

for idx, frame in enumerate(test_stream):
    b_status = baseline.update(frame)
    e_res = experimental.update(frame)
    
    print(f"{idx+1:<6} | {b_status:<20} | {e_res['status']:<25} | {e_res['penalty_score']:.4f}")

print("============================================")
