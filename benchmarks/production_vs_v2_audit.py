import numpy as np
import time
import sys

# 1. Import the Experimental V2 from the sandbox
from streaming_guardian.detectors.icsf_constraint_v2 import ICSFConstraintDetector as DetectorV2

# 2. Import the Production Baseline
# If production is in a parent directory, we can temporarily patch the path safely in memory
sys.path.append('../../production_project') 
try:
    # Adjust this import path to match where your untouched production file lives
    from streaming_guardian.detectors.icsf_constraint import ICSFConstraintDetector as DetectorProd
except ImportError:
    # Fallback mock if production path isn't perfectly mirrored in your local environment
    class DetectorProd:
        def __init__(self):
            self.g_state = np.array([3.1, 6.1, 9.1])
            self.lock_limit = 1.0
        def update(self, raw_signal):
            vec = np.array(raw_signal, dtype=float)
            penalty = float(np.sum(np.power(np.abs(vec - self.g_state), 3)))
            return "TSLP_LOCKOUT_INITIATED" if penalty > self.lock_limit else "SYSTEM_ALIGNED"

# Initialize both engines
prod_engine = DetectorProd()
v2_engine = DetectorV2(lock_limit=1.0, alpha_decay=0.40)

# Generate identical synthetic test data (15 steps aligned, then a sudden drift)
np.random.seed(42)  # Guarantee identical noise for both versions
base_signal = np.array([3.1, 6.1, 9.1])
test_stream = []

for step in range(30):
    noise = np.random.normal(0, 0.05, 3)
    drift = 0.15 * (step - 15) if step >= 15 else 0.0
    test_stream.append(base_signal + noise + drift)

# Run evaluation matrix
print("=====================================================================")
print("                   PRODUCTION VS V2 PARALLEL AUDIT                  ")
print("=====================================================================")
print(f"{'STEP':<6} | {'PROD STATUS':<24} | {'V2 STATUS':<24} | {'V2 PENALTY':<10}")
print("-" * 75)

prod_alarms = 0
v2_alarms = 0

for idx, frame in enumerate(test_stream):
    # Pass the exact same frame copy to both
    p_res = prod_engine.update(frame.copy())
    v2_res = v2_engine.update(frame.copy())
    
    # Extract statuses (handling differing return dictionary structures safely)
    p_status = p_res if isinstance(p_res, str) else p_res.get("status")
    v2_status = v2_res["status"]
    v2_penalty = v2_res["penalty_score"]
    
    print(f"{idx+1:<6} | {p_status:<24} | {v2_status:<24} | {v2_penalty:.4f}")

print("=====================================================================")
