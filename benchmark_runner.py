import numpy as np
import time
from distributed_core import DistributedAdaptiveCUSUM

def run_auditable_benchmark():
    print("==========================================================")
    print("      REGULATED BENCHMARK: ANTI-ENTROPY ENGINE EVAL       ")
    print("==========================================================")
    
    # 1. Establish deterministic environment (Fixed Seed)
    np.random.seed(42)
    stream_length = 200
    change_point = 100  # Exactly halfway, a slow drift is introduced
    
    # 2. Generate Synthetic Telemetry with Hidden Entropic Drift
    clean_signal = np.random.normal(loc=10.0, scale=1.0, size=stream_length)
    drift = np.zeros(stream_length)
    for i in range(change_point, stream_length):
        drift[i] = (i - change_point) * 0.15  # Linear degradation matrix
    
    test_stream = clean_signal + drift
    
    # 3. Initialize Engine
    detector = DistributedAdaptiveCUSUM(burn_in=30)
    state = {"history": [], "tracker": 0.0, "floor": 0.0, "step": 0}
    
    false_positives = 0
    true_positives = 0
    detection_index = None
    
    # 4. Execute Deterministic Evaluation Window
    start_time = time.perf_counter()
    for idx, val in enumerate(test_stream):
        is_anomaly, tracker, floor, step = detector.calculate_next_state(
            current_signal=val,
            state_history=state["history"],
            current_tracker=state["tracker"],
            current_floor=state["floor"],
            current_step=state["step"]
        )
        
        # Mutate state
        state["history"].append(val)
        state["tracker"] = tracker
        state["floor"] = floor
        state["step"] = step
        
        # Metrics Tracking
        if is_anomaly:
            if idx < change_point:
                false_positives += 1
            else:
                true_positives += 1
                if detection_index is None:
                    detection_index = idx

    execution_time = (time.perf_counter() - start_time) * 1000
    
    # 5. Calculate Standardized Metrics
    detection_delay = (detection_index - change_point) if detection_index else -1
    fpr = (false_positives / change_point) * 100
    
    print(f"\n[METRIC SUMMARY]")
    print(f"• Total Processed Packets : {stream_length}")
    print(f"• Math Engine Compute Time : {execution_time:.3f} ms")
    print(f"• False Positive Rate (FPR): {fpr:.2f}%")
    print(f"• True Anomaly Injected    : Packet index {change_point}")
    print(f"• Engine Alert Triggered   : Packet index {detection_index}")
    print(f"• Strict Detection Delay   : {detection_delay} packets")
    print("\n✅ Evaluation complete. Data is locked and reproducible.")

if __name__ == "__main__":
    run_auditable_benchmark()
