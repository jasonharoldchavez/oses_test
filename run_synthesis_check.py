import numpy as np
from streaming_guardian.detectors import ICSFConstraintDetector

print("=== STARTING EXPERT-LAYER SYNTHESIS CHECK ===")
try:
    engine = ICSFConstraintDetector(lock_limit=1.0)
    
    # Simulate a stream sequence to feed the predictive horizon and trend trackers
    stream_inputs = [
        [3.1, 6.1, 9.1],  # Stable starting point
        [3.2, 6.1, 9.0],
        [3.4, 6.2, 8.8],  # Slow trend developing
        [3.6, 6.3, 8.7]
    ]
    
    for idx, frame in enumerate(stream_inputs):
        res = engine.update(frame)
        print(f"\nStep {idx+1} | Input: {frame}")
        print(f" -> Status: {res['status']}")
        print(f" -> Symbolic Alignment: [{res['symbolic_chain']}]")
        print(f" -> Current Penalty: {res['penalty_score']} | Projected: {res['projected_penalty_3_steps']}")
        if res['patterns']:
            print(f" -> Patterns Found: {res['patterns']}")
            
except Exception as e:
    print(f"[X] Execution Failed: {e}")
print("\n=== EXPERT-LAYER SYNTHESIS COMPLETE ===")
