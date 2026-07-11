import numpy as np
from streaming_guardian.detectors.icsf_constraint import ICSFConstraintDetector

# Test an optimized version with a faster reaction time (lower alpha decay means less historical lag)
fast_experimental = ICSFConstraintDetector(lock_limit=1.0, alpha_decay=0.40)

test_stream = [[3.1 + (i * 0.05), 6.1, 9.1] for i in range(25)]

print("=== RUNNING TUNED REACTION AUDIT ===")
print(f"{'STEP':<6} | {'STATUS':<25} | {'PENALTY':<12} | {'PROJECTED':<12}")
print("-" * 65)

for idx, frame in enumerate(test_stream):
    res = fast_experimental.update(frame)
    print(f"{idx+1:<6} | {res['status']:<25} | {res['penalty_score']:.4f} | {res['projected_penalty_3_steps']:.4f}")

print("====================================")
